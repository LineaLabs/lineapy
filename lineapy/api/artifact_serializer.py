import logging
import types
from pathlib import Path
from typing import Any

from pandas.io.pickle import to_pickle

from lineapy.data.types import LineaID
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.plugins.utils import slugify
from lineapy.utils.analytics.event_schemas import (
    CatalogEvent,
    ErrorType,
    ExceptionEvent,
    GetEvent,
    SaveEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.config import options
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
# TODO: figure out if we need to configure it all the time
configure_logging()

def serialize_artifact(value_node_id: LineaID, execution_id: LineaID, reference:Any):

    pickle_name = _pickle_name(value_node_id, execution_id)
    _try_write_to_pickle(reference, pickle_name)
    

def _pickle_name(node_id: LineaID, execution_id: LineaID) -> str:
    """
    Pickle file for a value to be named with the following scheme.
    <node_id-hash>-<exec_id-hash>-pickle
    """
    return f"pre-{slugify(hash(node_id + execution_id))}-post.pkl"


def _try_write_to_pickle(value: object, filename: str) -> None:
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
