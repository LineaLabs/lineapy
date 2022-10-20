import logging
import types
from modulefinder import Module
from pathlib import Path
from typing import Any, Dict

from pandas.io.pickle import to_pickle

from lineapy.data.types import ML_MODELS_STORAGE_BACKEND, LineaID
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
configure_logging()

from inspect import getmodule

import mlflow
from sklearn.base import BaseEstimator

mlflow_io = {
    "sklearn": [
        {
            "class": BaseEstimator,
            "serializer": mlflow.sklearn.log_model,
            "deserializer": mlflow.sklearn.load_model,
        }
    ]
}


def serialize_artifact(
    value_node_id: LineaID,
    execution_id: LineaID,
    reference: Any,
    artifact_name: str,
    storage_backend,
) -> Dict[str, Any]:

    if options.get("mlflow_tracking_uri") is not None:
        if storage_backend == "mlflow" or (
            storage_backend is None
            and options.get("default_ml_models_storage_backend") == "mlflow"
        ):
            try:
                import mlflow
            except ModuleNotFoundError:
                logger.error(
                    "module 'mlflow' is not installed; please install it with 'pip install lineapy[mlflow]'"
                )

            mlflow.set_tracking_uri(options.get("mlflow_tracking_uri"))

            full_module_name = getmodule(reference)
            if full_module_name is not None:
                root_module_name = full_module_name.__name__.split(".")[0]
                if root_module_name in mlflow_io.keys():
                    for class_io in mlflow_io[root_module_name]:
                        if isinstance(reference, class_io["class"]):
                            model_info = class_io["serializer"](
                                reference, artifact_name
                            )
                            return {
                                "backend": "mlflow",
                                "metadata": model_info,
                            }

    pickle_name = _pickle_name(value_node_id, execution_id)
    _try_write_to_pickle(reference, pickle_name)
    return {
        "backend": "lineapy",
        "metadata": {"pickle_name": str(pickle_name)},
    }


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
