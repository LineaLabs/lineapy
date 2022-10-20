from pathlib import Path

from fsspec.core import url_to_fs
from fsspec.implementations.local import LocalFileSystem

from lineapy.utils.config import DEFAULT_ML_MODELS_STORAGE_BACKEND, options


def test_artifact_storage_dir_type():
    """
    Making sure the path we are setting is correct typing, so pandas.io.common.get_handler can process it correctly.
    """
    old_artifact_storage_dir = options.safe_get("artifact_storage_dir")
    options.set(
        "artifact_storage_dir",
        "/tmp/somelineapytestprefix/",
    )
    assert isinstance(
        url_to_fs(str(options.safe_get("artifact_storage_dir")))[0],
        LocalFileSystem,
    )

    options.set(
        "artifact_storage_dir",
        Path("~").expanduser().resolve(),
    )
    assert isinstance(
        url_to_fs(str(options.safe_get("artifact_storage_dir")))[0],
        LocalFileSystem,
    )

    options.set("artifact_storage_dir", old_artifact_storage_dir)


def test_mlflow_console_config():
    """
    Test mlflow config items from console
    """
    # By default both are None
    assert options.get("mlflow_tracking_uri") is None
    assert options.get("default_ml_models_storage_backend") is None
    # Specify only mlflow_tracking_uri, use DEFAULT_ML_MODELS_STORAGE_BACKEND
    options.set("mlflow_tracking_uri", "sqlite://")
    assert options.get("mlflow_tracking_uri") == "sqlite://"
    assert (
        options.get("default_ml_models_storage_backend")
        == DEFAULT_ML_MODELS_STORAGE_BACKEND
    )
    # Specify specific default_ml_models_storage_backend
    options.set("default_ml_models_storage_backend", "lineapy")
    assert options.get("default_ml_models_storage_backend") == "lineapy"
