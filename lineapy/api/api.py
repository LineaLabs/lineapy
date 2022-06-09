"""
User facing APIs.
"""

import logging
import os
import pickle
import random
import string
import types
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from lineapy.api.api_classes import LineaArtifact, LineaArtifactStore
from lineapy.data.types import Artifact, NodeValue, PipelineType
from lineapy.db.relational import SessionContextORM
from lineapy.db.utils import FilePickler, parse_artifact_version
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.exceptions.user_exception import UserException
from lineapy.execution.context import get_context
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.plugins.airflow import AirflowDagConfig, AirflowPlugin
from lineapy.plugins.script import ScriptPlugin
from lineapy.plugins.task import TaskGraphEdge
from lineapy.utils.analytics.event_schemas import (
    CatalogEvent,
    ExceptionEvent,
    GetEvent,
    SaveEvent,
    ToPipelineEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.analytics.utils import side_effect_to_str
from lineapy.utils.config import options
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import get_value_type

logger = logging.getLogger(__name__)
# TODO: figure out if we need to configure it all the time
configure_logging()

"""
Dev notes: We should keep these external APIs as small as possible, and unless
there is a very compelling use case, not support more than
one way to access the same feature.
"""


def save(reference: object, name: str) -> LineaArtifact:
    """
    Publishes the object to the Linea DB.

    Parameters
    ----------
    reference: Union[object, ExternalState]
        The reference could be a variable name, in which case Linea will save
        the value of the variable, with out default serialization mechanism.
        Alternatively, it could be a "side effect" reference, which currently includes either :class:`lineapy.file_system` or :class:`lineapy.db`.
        Linea will save the associated process that creates the final side effects.
        We are in the process of adding more side effect references, including `assert` statements.
    name: str
        The name is used for later retrieving the artifact and creating new versions if an artifact of the name has been created before.

    Returns
    -------
    LineaArtifact
        returned value offers methods to access
        information we have stored about the artifact (value, version), and other automation capabilities, such as :func:`to_pipeline`.
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
            track(ExceptionEvent("SaveAPI", msg))
            raise ValueError(msg)
    else:
        # Lookup the first arguments id, which is the id for the value, and
        # save that as the artifact
        value_node_id = call_node.positional_args[0].id

    execution_id = executor.execution.id
    timing = executor.get_execution_time(value_node_id)

    # serialize value to db if we haven't before
    # (happens with multiple artifacts pointing to the same value)
    if not db.node_value_in_db(
        node_id=value_node_id, execution_id=execution_id
    ):
        # can raise ArtifactSaveException

        # pickles value of artifact and saves to filesystem
        pickled_path = _try_write_to_db(reference)

        # adds reference to pickled file inside database
        db.write_node_value(
            NodeValue(
                node_id=value_node_id,
                value=str(pickled_path.resolve()),
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

    :param artifact_name: Key used to while saving the artifact
    :param version: version number or 'latest' or 'all'

    :raises ValueError: if arifact not found or version invalid
    """
    version = parse_artifact_version(version)

    # get database instance
    execution_context = get_context()
    executor = execution_context.executor
    db = executor.db

    # if version is 'all' or 'latest', get_version is None
    get_version = None if isinstance(version, str) else version

    try:
        artifact = db.get_artifact_by_name(artifact_name, version=get_version)
    except UserException:
        raise NameError(
            f"{artifact_name} not found. Perhaps there was a typo. Please try lineapy.artifact_store() to inspect all your artifacts."
        )

    node_id = artifact.node_id
    execution_id = artifact.execution_id

    db.delete_artifact_by_name(artifact_name, version=version)
    logging.info(f"Deleted Artifact: {artifact_name} version: {version}")

    try:
        db.delete_node_value_from_db(node_id, execution_id)
    except UserException:
        logging.info(
            f"Node: {node_id} with execution ID: {execution_id} not found in DB"
        )

    pickled_path = None
    try:
        pickled_path = db.get_node_value_path(node_id, execution_id)
    except ValueError:
        logging.debug(f"No valid pickle path found for {node_id}")

    if pickled_path is not None:
        try:
            _try_delete_pickle_file(Path(pickled_path))
        except KeyError:
            logging.debug(f"Pickle not found at {pickled_path}")
    else:
        logging.debug(f"No valid pickle path found for {node_id}")


def _try_delete_pickle_file(pickled_path: Path) -> None:
    if pickled_path.exists():
        pickled_path.unlink()
    else:
        # Attempt to reconstruct path to pickle with current
        # linea folder and pickle base directory.
        new_pickled_path = Path(
            options.safe_get("artifact_storage_dir")
        ).joinpath(pickled_path.name)
        if new_pickled_path.exists():
            new_pickled_path.unlink()
        else:
            raise KeyError(f"Pickle not found at {pickled_path}")


def _try_write_to_db(value: object) -> Path:
    """
    Saves the value to a random file inside linea folder. This file path is returned and eventually saved to the db.

    """
    if isinstance(value, types.ModuleType):
        raise ArtifactSaveException()
    # i think there's pretty low chance of clashes with 7 random chars but if it becomes one, just up the chars
    filepath = Path(options.safe_get("artifact_storage_dir")).joinpath(
        "".join(
            random.choices(
                string.ascii_uppercase
                + string.ascii_lowercase
                + string.digits,
                k=7,
            )
        )
    )
    try:
        os.makedirs(filepath.parent, exist_ok=True)
        with open(filepath, "wb") as f:
            FilePickler.dump(value, f)
    except pickle.PicklingError as pe:
        logger.error(pe)
        track(ExceptionEvent("ArtifactSaveException", str(pe)))
        raise ArtifactSaveException()
    return filepath


def get(artifact_name: str, version: Optional[int] = None) -> LineaArtifact:
    """
    Gets an artifact from the DB.

    Parameters
    ----------
    artifact_name: str
        name of the artifact. Note that if you do not remember the artifact,
        you can use the artifact_store to browse the options
    version: Optional[str]
        version of the artifact. If None, the latest version will be returned.

    Returns
    -------
    LineaArtifact
        returned value offers methods to access
        information we have stored about the artifact
    """
    validated_version = parse_artifact_version(version is None ? "latest":version)
    final_version = (
        validated_version if isinstance(validated_version, int) else None
    )

    execution_context = get_context()
    db = execution_context.executor.db
    artifact = db.get_artifact_by_name(artifact_name, final_version)
    linea_artifact = LineaArtifact(
        db=db,
        _execution_id=artifact.execution_id,
        _node_id=artifact.node_id,
        _session_id=artifact.node.session_id,
        _version=artifact.version,  # type: ignore
        name=artifact_name,
        date_created=artifact.date_created,  # type: ignore
    )

    track(GetEvent(version_specified=version is not None))
    return linea_artifact


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
    pipeline_dag_config: Optional[AirflowDagConfig] = {},
    output_dir: Optional[str] = None,
) -> Path:
    """
    Writes the pipeline job to a path on disk.

    :param artifacts: list of artifact names to be included in the DAG.
    :param framework: 'AIRFLOW' or 'SCRIPT'
    :param pipeline_name: name of the pipeline
    :param dependencies: tasks dependencies in graphlib format {'B':{'A','C'}},
        this means task A and C are prerequisites for task B.
    :param output_dir_path: Directory of the DAG and the python file it is
        saved in; only use for PipelineType.AIRFLOW
    :return: string containing the path of the DAG file that was exported.
    """
    execution_context = get_context()
    db = execution_context.executor.db
    session_orm = (
        db.session.query(SessionContextORM)
        .order_by(SessionContextORM.creation_time.desc())
        .all()
    )
    if len(session_orm) == 0:
        track(ExceptionEvent("DBError", "NoSessionFound"))
        raise Exception("No sessions found in the database.")
    last_session = session_orm[0]

    if framework in PipelineType.__members__:
        if PipelineType[framework] == PipelineType.AIRFLOW:

            ret = AirflowPlugin(db, last_session.id).sliced_airflow_dag(
                artifacts,
                pipeline_name,
                dependencies,
                output_dir=output_dir,
                airflow_dag_config=pipeline_dag_config,
            )

        else:

            ret = ScriptPlugin(db, last_session.id).sliced_pipeline_dag(
                artifacts,
                pipeline_name,
                dependencies,
                output_dir=output_dir,
            )

        # send the info
        track(
            ToPipelineEvent(
                framework,
                len(artifacts),
                dependencies != "",
                pipeline_dag_config is not None,
            )
        )
        return ret

    else:
        raise Exception(f"No PipelineType for {framework}")
