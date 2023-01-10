import json
import subprocess
import tempfile
from pathlib import Path

import pytest
from sklearn.base import BaseEstimator

mlflow = pytest.importorskip("mlflow")


@pytest.mark.slow
def test_save_get_delete_to_mlflow(execute):
    """
    Test mlflow as backend storage

    Test lineapy.save for mlflow, passing `registered_model_name` to test
    **kwargs. Test Artifact.get_value() for mlflow and validate model
    exists in MLflow.
    """
    code = """
import lineapy
import mlflow
lineapy.options.set('mlflow_tracking_uri','file:///tmp/mlruns')
lineapy.options.set('mlflow_registry_uri','sqlite://')
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(random_state=0)
X = [[ 1,  2,  3],  # 2 samples, 3 features
     [11, 12, 13]]
y = [0, 1]  # classes of each sample
clf.fit(X, y)
lineapy.save(clf, 'clf', registered_model_name='lineapy_clf')

art = lineapy.get('clf')
lineapy_model = art.get_value()

metadata = art.get_metadata()

client = mlflow.MlflowClient()
latest_version = client.search_model_versions("name='lineapy_clf'")[0].version
mlflow_model = mlflow.sklearn.load_model(f'models:/lineapy_clf/{latest_version}')

lineapy.delete('clf', version=art.version)
try:
    deleted_clf = lineapy.get('clf', version=art.version)
except:
    deleted_clf = None
lineapy.options.set('mlflow_tracking_uri',None)
lineapy.options.set('mlflow_registry_uri',None)
"""
    res = execute(code, snapshot=False)

    # Retrieve registered model from mlflow
    mlflow_model = res.values["mlflow_model"]
    assert isinstance(mlflow_model, BaseEstimator)

    # Retrieve model from Artifact.get_value()
    lineapy_model = res.values["lineapy_model"]
    assert isinstance(lineapy_model, BaseEstimator)

    # Metadata
    metadata = res.values["metadata"]
    assert "lineapy" in metadata.keys() and "mlflow" in metadata.keys()

    # Delete
    deleted_clf = res.values["deleted_clf"]
    assert deleted_clf is None


@pytest.mark.slow
def test_mlflow_config_with_cli():
    """
    Verify that `lineapy init` generate with different type of cli options input
    """
    temp_dir_name = tempfile.mkdtemp()
    subprocess.check_call(
        [
            "lineapy",
            "--home-dir",
            temp_dir_name,
            "--mlflow-tracking-uri=sqlite://",
            "--default-ml-models-storage-backend=mlflow",
            "init",
        ]
    )

    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)

    assert Path(temp_dir_name).joinpath("lineapy_config.json").exists()
    assert generated_config["home_dir"] == temp_dir_name
    assert generated_config["mlflow_tracking_uri"] == "sqlite://"
    assert generated_config["default_ml_models_storage_backend"] == "mlflow"
