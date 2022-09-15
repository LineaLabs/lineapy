"""
User facing APIs.
"""

import logging
import types
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import fsspec
from pandas.io.pickle import to_pickle

from lineapy.api.api_classes import LineaArtifact, LineaArtifactStore
from lineapy.data.types import Artifact, LineaID, NodeValue, PipelineType
from lineapy.db.relational import SessionContextORM
from lineapy.db.utils import parse_artifact_version
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.exceptions.user_exception import UserException
from lineapy.execution.context import get_context
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.plugins.airflow import AirflowDagConfig, AirflowPlugin
from lineapy.plugins.script import ScriptPlugin
from lineapy.plugins.task import TaskGraphEdge
from lineapy.plugins.utils import slugify
from lineapy.utils.analytics.event_schemas import (
    CatalogEvent,
    ErrorType,
    ExceptionEvent,
    GetEvent,
    SaveEvent,
    ToPipelineEvent,
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
    logger.warn("Calling save inside control blocks is not supported")


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
            f"{artifact_name}:{version} not found. Perhaps there was a typo. Please try lineapy.artifact_store() to inspect all your artifacts."
        )

    node_id = artifact.node_id
    execution_id = artifact.execution_id

    pickled_path = None
    try:
        pickled_name = db.get_node_value_path(node_id, execution_id)
        pickled_path = (
            str(options.safe_get("artifact_storage_dir")).rstrip("/")
            + f"/{pickled_name}"
        )
        # Wrap the db operation and file as a transaction
        with fsspec.open(pickled_path) as f:
            db.delete_artifact_by_name(artifact_name, version=version)
            logging.info(
                f"Deleted Artifact: {artifact_name} version: {version}"
            )
            try:
                db.delete_node_value_from_db(node_id, execution_id)
            except UserException:
                logging.info(
                    f"Node: {node_id} with execution ID: {execution_id} not found in DB"
                )
            f.fs.delete(f.path)
    except ValueError:
        logging.debug(f"No valid pickle path found for {node_id}")



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
    logger.warn("cant use get inside blackbox")


def reload() -> None:
    """
    Reloads lineapy context.

    .. note::

        Currently only reloads annotations but in the future can be a container for other items like configs etc.

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
    logger.warn("Cant use artifact_store in blackboxes")


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
        track(ExceptionEvent(ErrorType.PIPELINE, "No session found in DB"))
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
