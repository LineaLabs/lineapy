"""
User facing APIs.
"""

import os
import pickle
import random
import string
import types
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from lineapy.data.types import Artifact, NodeValue, PipelineType
from lineapy.db.relational import SessionContextORM
from lineapy.db.utils import FILE_PICKLER_BASEDIR, FilePickler
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.execution.context import get_context
from lineapy.graph_reader.apis import LineaArtifact, LineaCatalog
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.plugins.airflow import AirflowDagConfig, AirflowPlugin
from lineapy.plugins.script import ScriptPlugin
from lineapy.utils.config import linea_folder
from lineapy.utils.utils import get_value_type

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
        information we have stored about the artifact (value, version), and other automation capabilities, such as :func:`to_airflow`.
    """
    execution_context = get_context()
    executor = execution_context.executor
    db = executor.db
    call_node = execution_context.node

    # If this value is stored as a global in the executor (meaning its an external side effect)
    # then look it up from there, instead of using this node.
    if isinstance(reference, ExternalState):
        value_node_id = executor.lookup_external_state(reference)
        if not value_node_id:
            raise ValueError(
                f"No change to the {reference.external_state} was recorded. If it was in fact changed, please open a Github issue."
            )
    else:
        # Lookup the first arguments id, which is the id for the value, and
        # save that as the artifact
        value_node_id = call_node.positional_args[0].id

    execution_id = executor.execution.id
    timing = executor.get_execution_time(value_node_id)

    linea_artifact = LineaArtifact(
        db=db,
        execution_id=execution_id,
        node_id=value_node_id,
        session_id=call_node.session_id,
        name=name,
    )

    # serialize value to db if we haven't before
    # (happens with multiple artifacts pointing to the same value)
    if not db.node_value_in_db(
        node_id=value_node_id, execution_id=execution_id
    ):
        # can raise ArtifactSaveException
        pickled_path = _try_write_to_db(reference)
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
    # If we have already saved this same artifact, with the same name,
    # then don't write it again.
    if not db.artifact_in_db(
        node_id=value_node_id,
        execution_id=execution_id,
        name=name,
        version=linea_artifact.version,
    ):
        artifact_to_write = Artifact(
            node_id=value_node_id,
            execution_id=execution_id,
            date_created=datetime.now(),
            name=name,
            version=linea_artifact.version,
        )
        db.write_artifact(artifact_to_write)
        linea_artifact.date_created = artifact_to_write.date_created

    return linea_artifact


def _try_write_to_db(value: object) -> Path:
    """
    Saves the value to a random file inside linea folder. This file path is returned and eventually saved to the db.

    """
    if isinstance(value, types.ModuleType):
        raise ArtifactSaveException()
    # i think there's pretty low chance of clashes with 7 random chars but if it becomes one, just up the chars
    filepath = (
        linea_folder()
        / FILE_PICKLER_BASEDIR
        / "".join(
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
        print(pe)
        raise ArtifactSaveException()
    return filepath


def get(artifact_name: str, version: Optional[str] = None) -> LineaArtifact:
    """
    Gets an artifact from the DB.

    Parameters
    ----------
    artifact_name: str
        name of the artifact. Note that if you do not remember the artifact,
        you can use the catalog to browse the options
    version: Optional[str]
        version of the artifact. If None, the latest version will be returned.

    Returns
    -------
    LineaArtifact
        returned value offers methods to access
        information we have stored about the artifact
    """
    execution_context = get_context()
    db = execution_context.executor.db
    artifact = db.get_artifact_by_name(artifact_name, version)
    linea_artifact = LineaArtifact(
        db=db,
        execution_id=artifact.execution_id,
        node_id=artifact.node_id,
        session_id=artifact.node.session_id,
        name=artifact_name,
        date_created=artifact.date_created,
    )
    # doing this thing because we dont initialize the version when defining LineaArtifact
    if artifact.version:
        linea_artifact.version = artifact.version

    return linea_artifact


def catalog() -> LineaCatalog:
    """
    Returns
    -------
    LineaCatalog
        An object of the class `LineaCatalog` that allows for printing and exporting artifacts metadata.
    """
    execution_context = get_context()
    return LineaCatalog(execution_context.executor.db)


# TODO - this piece needs to test more than just the output of jupyter cell.
# we need to ensure all the required files (python module and the dag file) get written to the right place.
def to_pipeline(
    artifacts: List[str],
    framework: str = "SCRIPT",
    pipeline_name: Optional[str] = None,
    dependencies: str = "",
    pipeline_dag_config: AirflowDagConfig = {},
    output_dir: Optional[str] = None,
) -> Path:
    """
    Writes the pipeline job to a path on disk.

    :param artifacts: list of artifact names to be included in the DAG.
    :param framework: 'AIRFLOW' or 'SCRIPT'
    :param pipeline_name: name of the pipeline
    :param dependencies: task dependencies in Airflow format,
                                      i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
                                      This translates to "p_value >> y" and "p_value, x >> y" respectively.
                                      Here "p_value" and "x" are independent tasks
                                      and "y" depends on them.
    :param output_dir_path: Directory of the DAG and the python file it is saved in; only use for PipelineType.AIRFLOW
    :return: string containing the path of the Airflow DAG file that was exported.
    """
    execution_context = get_context()
    db = execution_context.executor.db
    session_orm = db.session.query(SessionContextORM).all()
    if len(session_orm) == 0:
        raise Exception("No sessions found in the database.")
    last_session = session_orm[0]

    if framework in PipelineType.__members__:
        if PipelineType[framework] == PipelineType.AIRFLOW:

            return AirflowPlugin(db, last_session.id).sliced_airflow_dag(
                artifacts,
                pipeline_name,
                dependencies,
                output_dir=output_dir,
                airflow_dag_config=pipeline_dag_config,
            )

        else:

            return ScriptPlugin(db, last_session.id).sliced_pipeline_dag(
                artifacts,
                pipeline_name,
                dependencies,
                output_dir=output_dir,
            )

    else:
        raise Exception(f"No PipelineType for {framework}")
