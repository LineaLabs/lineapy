import os

import pytest

from lineapy.utils.config import DEFAULT_ML_MODELS_STORAGE_BACKEND, options
from tests.util import clean_lineapy_env_var

mlflow = pytest.importorskip("mlflow")


def test_mlflow_console_config():
    """
    Test mlflow config items from console
    """
    # Reset config
    existing_lineapy_env = clean_lineapy_env_var()
    options.set("mlflow_tracking_uri", None)
    options.set("mlflow_registry_uri", None)
    options.set("default_ml_models_storage_backend", None)

    # By default both are None
    assert options.get("mlflow_tracking_uri") is None
    assert options.get("mlflow_registry_uri") is None
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

    # Reset to original env variables
    clean_lineapy_env_var()
    for k, v in existing_lineapy_env.items():
        os.environ[k] = v

    # Reset MLFlow options to not affect subsequent tests
    options.set("mlflow_tracking_uri", None)
    options.set("default_ml_models_storage_backend", None)
