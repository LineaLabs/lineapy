import logging
import types
from pathlib import Path
from typing import Any, Dict, Optional

from lineapy.api.api_utils import to_pickle
from lineapy.data.types import ARTIFACT_STORAGE_BACKEND, LineaID
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.plugins.serializers.mlflow_io import try_write_to_mlflow
from lineapy.plugins.utils import slugify
from lineapy.utils.analytics.event_schemas import ErrorType, ExceptionEvent
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.config import options
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


def serialize_artifact(
    value_node_id: LineaID,
    execution_id: LineaID,
    reference: Any,
    name: str,
    storage_backend: Optional[ARTIFACT_STORAGE_BACKEND] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Serialize artifact using various backend.

    Currently, most objects are using lineapy as the backend for serialization.
    The only exception is MLflow-supported model flavors. In order to use
    MLflow for ml model serialization, following conditions need to be
    satisfied:

    1. The artifact(ML model) should be a MLflow-supported flavor
    2. MLflow is installed
    3. `storage_backend` should be `mlflow` or `storage_backend` is `None` and
    `options.get("default_ARTIFACT_STORAGE_BACKEND")=='mlflow'`

    Parameters
    ----------
    value_node_id: LineaID
        Value node id in Linea Graph
    execution_id: LineaID
        Execution id
    reference: Union[object, ExternalState]
        Same as reference in [`lineapy.save()`][lineapy.api.api.save]
    name: str
        Same as reference in [`lineapy.save()`][lineapy.api.api.save]
    storage_backend: Optional[ARTIFACT_STORAGE_BACKEND]
        Same as reference in [`lineapy.save()`][lineapy.api.api.save]
    **kwargs:
        Same as reference in [`lineapy.save()`][lineapy.api.api.save]

    Returns
    -------
    Dict
        Dictionary with following key-value pair:

        - backend: storage backend used to save the artifact
        - metadata: metadata of the storage backed
    """
    if _able_to_use_mlflow(storage_backend):
        model_info = try_write_to_mlflow(reference, name, **kwargs)
        if model_info is not None:
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


def _able_to_use_mlflow(storage_backend) -> bool:
    """
    Determine whether to use MLflow to serialize ML models.

    Use MLflow if

    1. config `mlflow_tracking_uri` is not empty
    2. `storage_backend=='mlflow'` or (`storage_backend is None` and
        `default_ml_models_storage_backend` is mlflow)

    Parameters
    ----------
    storage_backend: Optional[ARTIFACT_STORAGE_BACKEND]
        Same as reference in [`lineapy.save()`][lineapy.api.api.save]

    Returns
    -------
    bool
    """
    if options.get("mlflow_tracking_uri") is not None:
        if storage_backend == ARTIFACT_STORAGE_BACKEND.mlflow or (
            storage_backend is None
            and options.get("default_ml_models_storage_backend")
            == ARTIFACT_STORAGE_BACKEND.mlflow
        ):
            return True
    return False


def _pickle_name(node_id: LineaID, execution_id: LineaID) -> str:
    """
    Pickle file for a value to be named with the following scheme.
    <node_id-hash>-<exec_id-hash>-pickle
    """
    return f"pre-{slugify(hash(node_id + execution_id))}-post.pkl"


def _try_write_to_pickle(value: object, filename: str) -> None:
    """
    Saves the value to a random file inside linea folder.
    This file path is returned and eventually saved to the db.

    Parameters
    ----------
    value: object
        Data to pickle
    filename: str
        Name of pickle file
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
