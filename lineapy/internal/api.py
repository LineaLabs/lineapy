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


def _save(
    call_node, executor, db, reference: object, name: str
) -> LineaArtifact:
    # execution_context = get_context()
    # executor = execution_context.executor
    # db = executor.db
    # call_node = execution_context.node

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
    if not db.node_value_in_db(
        node_id=value_node_id, execution_id=execution_id
    ):

        # TODO add version or timestamp to allow saving of multiple pickle files for the same node id
        # pickles value of artifact and saves to filesystem
        pickle_name = _pickle_name(value_node_id, execution_id)
        try_write_to_pickle(reference, pickle_name)

        # adds reference to pickled file inside database
        db.write_node_value(
            NodeValue(
                node_id=value_node_id,
                value=str(pickle_name),
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


def _get(
    call_node, executor, db, artifact_name: str, version: Optional[int] = None
) -> LineaArtifact:
    validated_version = parse_artifact_version(
        "latest" if version is None else version
    )
    final_version = (
        validated_version if isinstance(validated_version, int) else None
    )

    # execution_context = get_context()
    # db = execution_context.executor.db
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


def _artifact_store(_call_node, _executor, db) -> LineaArtifactStore:
    cat = LineaArtifactStore(db)
    track(CatalogEvent(catalog_size=cat.len))
    return cat


def _pickle_name(node_id: LineaID, execution_id: LineaID) -> str:
    """
    Pickle file for a value to be named with the following scheme.
    <node_id-hash>-<exec_id-hash>-pickle
    """
    return f"pre-{slugify(hash(node_id + execution_id))}-post.pkl"


def try_write_to_pickle(value: object, filename: str) -> None:
    """
    Saves the value to a random file inside linea folder. This file path is returned and eventually saved to the db.

    :param value: data to pickle
    :param filename: name of pickle file
    """
    if isinstance(value, types.ModuleType):
        track(ExceptionEvent(ErrorType.SAVE, "Invalid type for artifact"))
        raise ArtifactSaveException(
            "Lineapy does not support saving Python Module Objects as pickles"
        )

    artifact_storage_dir = options.safe_get("artifact_storage_dir")
    filepath = (
        artifact_storage_dir.joinpath(filename)
        if isinstance(artifact_storage_dir, Path)
        else f'{artifact_storage_dir.rstrip("/")}/{filename}'
    )
    try:
        logger.debug(f"Saving file to {filepath} ")
        to_pickle(
            value, filepath, storage_options=options.get("storage_options")
        )
    except Exception as e:
        # Don't see an easy way to catch all possible exceptions from the to_pickle, so just catch everything for now
        logger.error(e)
        track(ExceptionEvent(ErrorType.SAVE, "Pickling error"))
        raise e


def healthcheck(*args, **kwargs):
    print(args)
    print(kwargs)
