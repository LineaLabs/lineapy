"""
User-facing APIs.
"""

import logging
import warnings
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional, Tuple, Union

import fsspec

from lineapy.api.artifact_serializer import serialize_artifact
from lineapy.api.models.linea_artifact import LineaArtifact
from lineapy.api.models.linea_artifact_store import LineaArtifactStore
from lineapy.api.models.pipeline import Pipeline
from lineapy.data.types import ARTIFACT_STORAGE_BACKEND, Artifact, NodeValue
from lineapy.db.utils import parse_artifact_version
from lineapy.exceptions.user_exception import UserException
from lineapy.execution.context import get_context
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.plugins.base_pipeline_writer import get_basepipelinewriter
from lineapy.plugins.loader import load_as_module
from lineapy.plugins.task import TaskGraphEdge
from lineapy.utils.analytics.event_schemas import (
    CatalogEvent,
    ErrorType,
    ExceptionEvent,
    GetEvent,
    SaveEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.analytics.utils import side_effect_to_str
from lineapy.utils.config import options
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import get_system_python_version, get_value_type

logger = logging.getLogger(__name__)
# TODO: figure out if we need to configure it all the time
configure_logging()

"""
Dev notes: We should keep these external APIs as small as possible, and unless
there is a very compelling use case, not support more than
one way to access the same feature.
"""


def save(
    reference: object,
    name: str,
    storage_backend: Optional[ARTIFACT_STORAGE_BACKEND] = None,
    **kwargs,
) -> LineaArtifact:
    """
    Publishes the object to the LineaPy DB.

    Parameters
    ----------
    reference: Union[object, ExternalState]
        The reference could be a variable name, in which case LineaPy will save
        the value of the variable, with out default serialization mechanism.
        Alternatively, it could be a "side effect" reference, which currently includes either `lineapy.file_system` or `lineapy.db`.
        LineaPy will save the associated process that creates the final side effects.
        We are in the process of adding more side effect references, including `assert` statements.
    name: str
        The name is used for later retrieving the artifact and creating new versions if an artifact of the name has been created before.
    storage_backend: Optional[ARTIFACT_STORAGE_BACKEND]
        The storage backend used to save the artifact. Currently support
        lineapy and mlflow (for mlflow supported model flavors). In case of
        mlflow, lineapy will use `mlflow.sklearn.log_model` or other supported
        flavors equivalent to save artifacts into mlflow.
    **kwargs:
        Keyword arguments passed into underlying storage mechanism to overwrite
        default behavior. For `storage_backend='mlflow'`, this can overwrite
        default arguments in the `mlflow.sklearn.log_model` or other supported
        flavors equivalent.

    Returns
    -------
    LineaArtifact
        Returned value offers methods to access
        information we have stored about the artifact (value, version),
        and other automation capabilities, such as [`to_pipeline()`][lineapy.api.api.to_pipeline].
    """
    execution_context = get_context()
    executor = execution_context.executor
    db = executor.db
    call_node = execution_context.node

    # If this value is stored as a global in the executor (meaning its an external side effect)
    # then look it up from there, instead of using this node.
    if isinstance(reference, ExternalState):
        value_node_id = executor.lookup_external_state(reference)
        msg = f"No change to the {reference.external_state} was recorded. If it was in fact changed, please open a Github issue."
        if not value_node_id:
            track(
                ExceptionEvent(ErrorType.SAVE, "No change to external state")
            )
            raise ValueError(msg)
    else:
        # Lookup the first arguments id, which is the id for the value, and
        # save that as the artifact
        value_node_id = call_node.positional_args[0].id

    execution_id = executor.execution.id
    timing = executor.get_execution_time(value_node_id)

    # serialize value to db if we haven't before
    # (happens with multiple artifacts pointing to the same value)
    serialize_method = ARTIFACT_STORAGE_BACKEND.lineapy
    if not db.node_value_in_db(
        node_id=value_node_id, execution_id=execution_id
    ):

        # TODO add version or timestamp to allow saving of multiple pickle files for the same node id

        artifact_serialize_metadata = serialize_artifact(
            value_node_id,
            execution_id,
            reference,
            name,
            storage_backend,
            **kwargs,
        )
        if (
            artifact_serialize_metadata["backend"]
            == ARTIFACT_STORAGE_BACKEND.mlflow
        ):
            artifact_path = artifact_serialize_metadata["metadata"].model_uri
            serialize_method = ARTIFACT_STORAGE_BACKEND.mlflow
        else:
            artifact_path = artifact_serialize_metadata["metadata"][
                "pickle_name"
            ]

        # adds reference to pickled file inside database
        db.write_node_value(
            NodeValue(
                node_id=value_node_id,
                value=artifact_path,
                execution_id=execution_id,
                start_time=timing[0],
                end_time=timing[1],
                value_type=get_value_type(reference),
            )
        )
        # we have to commit eagerly because if we just add it
        #   to the queue, the `res` value may have mutated
        #   and that's incorrect.
        db.commit()

    # artifact_version = 0 if artifact exists else bump one version
    date_created = datetime.utcnow()
    artifact_version = db.get_latest_artifact_version(name) + 1

    artifact_to_write = Artifact(
        node_id=value_node_id,
        execution_id=execution_id,
        date_created=date_created,
        name=name,
        version=artifact_version,
    )
    db.write_artifact(artifact_to_write)

    if serialize_method == ARTIFACT_STORAGE_BACKEND.mlflow:
        artifactorm = db.get_artifactorm_by_name(
            artifact_name=name, version=artifact_version
        )
        db.write_mlflow_artifactmetadata(
            artifactorm, artifact_serialize_metadata["metadata"]
        )

    track(SaveEvent(side_effect=side_effect_to_str(reference)))

    linea_artifact = LineaArtifact(
        db=db,
        name=name,
        date_created=date_created,
        _execution_id=execution_id,
        _node_id=value_node_id,
        _session_id=call_node.session_id,
        _version=artifact_version,
    )
    return linea_artifact


def delete(artifact_name: str, version: Union[int, str]) -> None:
    """
    Deletes an artifact from artifact store. If no other artifacts
    refer to the value, the value is also deleted from both the
    value node store and the pickle store.

    Parameters
    ----------
    artifact_name: str
        Key used to while saving the artifact.
    version: Union[int, str]
        Version number or "latest" or "all".

    Raises
    ------
    ValueError
        If artifact not found or version invalid.
    """
    version = parse_artifact_version(version)

    # get database instance
    execution_context = get_context()
    executor = execution_context.executor
    db = executor.db

    # if version is 'all' or 'latest', get_version is None
    get_version = None if isinstance(version, str) else version

    try:
        metadata = get(artifact_name, get_version).get_metadata()
    except UserException:
        raise NameError(
            f"{artifact_name}:{version} not found. Perhaps there was a typo. Please try lineapy.artifact_store() to inspect all your artifacts."
        )

    lineapy_metadata = metadata["lineapy"]
    node_id = lineapy_metadata.node_id
    execution_id = lineapy_metadata.execution_id

    db.delete_artifact_by_name(artifact_name, version=version)
    logging.info(f"Deleted Artifact: {artifact_name} version: {version}")
    try:
        db.delete_node_value_from_db(node_id, execution_id)
    except UserException:
        logging.info(
            f"Node: {node_id} with execution ID: {execution_id} not found in DB"
        )
    except ValueError:
        logging.debug(f"No valid storage path found for {node_id}")

    if lineapy_metadata.storage_backend == ARTIFACT_STORAGE_BACKEND.lineapy:
        storage_path = lineapy_metadata.storage_path
        pickled_path = (
            str(options.safe_get("artifact_storage_dir")).rstrip("/")
            + f"/{storage_path}"
        )
        with fsspec.open(pickled_path) as f:
            f.fs.delete(f.path)
    elif lineapy_metadata.storage_backend == ARTIFACT_STORAGE_BACKEND.mlflow:
        try:
            db.delete_mlflow_metadata_by_artifact_id(
                lineapy_metadata.artifact_id
            )
        except UserException:
            logging.info(
                f"Artifact id {lineapy_metadata.artifact_id} is not found in DB"
            )


def get(artifact_name: str, version: Optional[int] = None) -> LineaArtifact:
    """
    Gets an artifact from the DB.

    Parameters
    ----------
    artifact_name: str
        Name of the artifact. Note that if you do not remember the artifact,
        you can use the artifact_store to browse the options.
    version: Optional[str]
        Version of the artifact. If `None`, the latest version will be returned.

    Returns
    -------
    LineaArtifact
        Returned value offers methods to access
        information we have stored about the artifact.
    """
    validated_version = parse_artifact_version(
        "latest" if version is None else version
    )
    final_version = (
        validated_version if isinstance(validated_version, int) else None
    )

    execution_context = get_context()
    db = execution_context.executor.db
    artifactorm = db.get_artifactorm_by_name(artifact_name, final_version)
    linea_artifact = LineaArtifact(
        db=db,
        _artifact_id=artifactorm.id,
        _execution_id=artifactorm.execution_id,
        _node_id=artifactorm.node_id,
        _session_id=artifactorm.node.session_id,
        _version=artifactorm.version,  # type: ignore
        name=artifact_name,
        date_created=artifactorm.date_created,  # type: ignore
    )

    # Check version compatibility
    system_python_version = get_system_python_version()  # up to minor version
    artifact_python_version = db.get_session_context(
        linea_artifact._session_id
    ).python_version
    if system_python_version != artifact_python_version:
        warnings.warn(
            f"Current session runs on Python {system_python_version}, but the retrieved artifact was created on Python {artifact_python_version}. This may result in incompatibility issues."
        )

    track(GetEvent(version_specified=version is not None))
    return linea_artifact


def get_pipeline(name: str) -> Pipeline:

    execution_context = get_context()
    db = execution_context.executor.db

    pipeline_orm = db.get_pipeline_by_name(name)

    artifact_names = [
        artifact.name
        for artifact in pipeline_orm.artifacts
        if artifact.name is not None
    ]

    dependencies = dict()
    for dep_orm in pipeline_orm.dependencies:
        post_artifact = dep_orm.post_artifact
        if post_artifact is None:
            continue
        post_name = post_artifact.name
        if post_name is None:
            continue

        pre_names = set(
            [
                pre_art.name
                for pre_art in dep_orm.pre_artifacts
                if pre_art.name is not None
            ]
        )
        dependencies[post_name] = pre_names
    return Pipeline(
        artifacts=artifact_names,
        name=name,
        dependencies=dependencies,
    )


def reload() -> None:
    """
    Reloads lineapy context.

    !!! note

        Currently only reloads annotations but in the future can be a container
        for other items like configs, etc.
    """
    execution_context = get_context()
    execution_context.executor.reload_annotations()


def artifact_store() -> LineaArtifactStore:
    """
    Returns
    -------
    LineaArtifactStore
        An object of the class `LineaArtifactStore` that allows for printing and exporting artifacts metadata.
    """
    execution_context = get_context()
    cat = LineaArtifactStore(execution_context.executor.db)
    track(CatalogEvent(catalog_size=cat.len))
    return cat


# TODO - this piece needs to test more than just the output of jupyter cell.
# we need to ensure all the required files (python module and the dag file) get written to the right place.
def to_pipeline(
    artifacts: List[str],
    framework: str = "SCRIPT",
    pipeline_name: Optional[str] = None,
    dependencies: TaskGraphEdge = {},
    output_dir: str = ".",
    input_parameters: List[str] = [],
    reuse_pre_computed_artifacts: List[str] = [],
    generate_test: bool = False,
    pipeline_dag_config: Optional[Dict] = {},
    include_non_slice_as_comment: bool = False,
) -> Path:
    """
    Writes the pipeline job to a path on disk.

    Parameters
    ----------
    artifacts: List[str]
        Names of artifacts to be included in the pipeline.
    framework: str
        Name of the framework to be used.
        Defined by enum PipelineTypes in lineapy/data/types.py.
        Defaults to "SCRIPT" if not specified.
    pipeline_name: Optional[str]
        Name of the pipeline.
    dependencies: TaskGraphEdge
        Task dependencies in graphlib format, e.g., ``{"B": {"A", "C"}}``
        means task A and C are prerequisites for task B.
        LineaPy is smart enough to figure out dependency relations *within*
        the same session, so there is no need to specify this type of dependency
        information; instead, the user is expected to provide dependency information
        among artifacts across different sessions.
    output_dir: str
        Directory path to save DAG and other pipeline files.
    input_parameters: List[str]
        Names of variables to be used as parameters in the pipeline.
        Currently, it only accepts variables from literal assignment
        such as ``a = '123'``. For each variable to be parametrized,
        there should be only one literal assignment across all
        artifact code for the pipeline. For instance, if both ``a = '123'``
        and ``a = 'abc'`` exist in the pipeline's artifact code,
        we cannot make ``a`` an input parameter since its reference is
        ambiguous, i.e., we are not sure which literal assignment ``a``
        refers to.
    reuse_pre_computed_artifacts: List[str]
        Names of artifacts in the pipeline for which pre-computed value
        is to be used (rather than recomputing the value).
    generate_test: bool
        Whether to generate scaffold/template for pipeline testing.
        Defaults to ``False``. The scaffold contains placeholders for testing
        each function in the pipeline module file and is meant to be fleshed
        out by the user to suit their needs. When run out of the box, it performs
        a naive form of equality evaluation for each function's output,
        which demands validation and customization by the user.
    pipeline_dag_config: Optional[AirflowDagConfig]
        A dictionary of parameters to configure DAG file to be generated.
        Not applicable for "SCRIPT" framework as it does not generate a separate
        DAG file. For "AIRFLOW" framework, Airflow-native config params such as
        "retries" and "schedule_interval" can be passed in. For "ARGO" framework,
        Argo-native config params such as "namespace" and "service_account_name".

    Returns
    -------
    Path
        Directory path where DAG and other pipeline files are saved.
    """
    pipeline = Pipeline(
        artifacts=artifacts,
        name=pipeline_name,
        dependencies=dependencies,
    )
    pipeline.save()
    return pipeline.export(
        framework=framework,
        output_dir=output_dir,
        input_parameters=input_parameters,
        reuse_pre_computed_artifacts=reuse_pre_computed_artifacts,
        generate_test=generate_test,
        pipeline_dag_config=pipeline_dag_config,
        include_non_slice_as_comment=include_non_slice_as_comment,
    )


def create_pipeline(
    artifacts: List[str],
    pipeline_name: Optional[str] = None,
    dependencies: TaskGraphEdge = {},
    persist: bool = False,
) -> Pipeline:
    pipeline = Pipeline(
        artifacts=artifacts,
        name=pipeline_name,
        dependencies=dependencies,
    )
    if persist:
        pipeline.save()

    return pipeline


def get_function(
    artifacts: List[Union[str, Tuple[str, int]]],
    input_parameters: List[str] = [],
    reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]] = [],
) -> Callable:
    """
    Extract the process that creates selected artifacts as a python function

    Parameters
    ----------
    artifacts: List[Union[str, Tuple[str, int]]]
        List of artifact names (with optional version) to be included in the
        function return.
    input_parameters: List[str]
        List of variable names to be used in the function arguments. Currently,
        only accept variable from literal assignment; such as a='123'. There
        should be only one literal assignment for each variable within all
        artifact calculation code. For instance, if both a='123' and a='abc'
        are existing in the code, we cannot specify a as input variables since
        it is confusing to specify which literal assignment we want to replace.
    reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]]
        List of artifacts(name with optional version) for which we will use
        pre-computed values from the artifact store instead of recomputing from
        original code.

    Returns
    -------
    Callable
        A python function that takes input_parameters as args and returns a
        dictionary with each artifact name as the dictionary key and artifact
        value as the value.

    Note that:

    1. If an input parameter is only used to calculate artifacts in the
        `reuse_pre_computed_artifacts` list, that input parameter will be
        passed around as a dummy variable. LineaPy will create a warning.
    2. If an artifact name has been saved multiple times within a session,
        multiple sessions or mutated. You might want to specify version
        number in `artifacts` or `reuse_pre_computed_artifacts`. The best
        practice to avoid searching artifact version is don't reuse artifact
        name in different notebooks and don't save same artifact multiple times
        within the same session.
    """
    module = get_module(
        artifacts, input_parameters, reuse_pre_computed_artifacts
    )
    return module.run_all_sessions


def get_module_definition(
    artifacts: List[Union[str, Tuple[str, int]]],
    input_parameters: List[str] = [],
    reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]] = [],
) -> str:
    """
    Get the python module definition for [`get_module()`][lineapy.api.api.get_module].

    Parameters
    ----------
    artifacts: List[Union[str, Tuple[str, int]]]
        Same as in [`get_function()`][lineapy.api.api.get_function].
    input_parameters: List[str]
        Same as in [`get_function()`][lineapy.api.api.get_function].
    reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]]
        Same as in [`get_function()`][lineapy.api.api.get_function].

    Returns
    -------
    str
        Module definition of [`get_module()`][lineapy.api.api.get_module].
    """
    writer = get_basepipelinewriter(
        artifacts, input_parameters, reuse_pre_computed_artifacts
    )
    return writer._compose_module()


def get_module(
    artifacts: List[Union[str, Tuple[str, int]]],
    input_parameters: List[str] = [],
    reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]] = [],
) -> ModuleType:
    """
    Create a python module that includes the definition of [`get_function()`][lineapy.api.api.get_function].

    Parameters
    ----------
    artifacts: List[Union[str, Tuple[str, int]]]
        Same as in [`get_function()`][lineapy.api.api.get_function].
    input_parameters: List[str]
        Same as in [`get_function()`][lineapy.api.api.get_function].
    reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]]
        Same as in [`get_function()`][lineapy.api.api.get_function].

    Returns
    -------
    str
        A python module that includes the definition of [`get_function()`][lineapy.api.api.get_function]
        as `run_all_sessions`.
    """
    writer = get_basepipelinewriter(
        artifacts, input_parameters, reuse_pre_computed_artifacts
    )
    module = load_as_module(writer)
    return module
