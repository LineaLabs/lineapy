import json
import subprocess
import tempfile
from pathlib import Path

import pytest
from sklearn.base import BaseEstimator

mlflow = pytest.importorskip("mlflow")


def test_save_to_mlflow(execute):
    """
    Test lienapy.save to mlflow, passing `registered_model_name` to test **kwargs.
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
client = mlflow.MlflowClient()
latest_version = client.search_model_versions("name='lineapy_clf'")[0].version
mlflow_model = mlflow.sklearn.load_model(f'models:/lineapy_clf/{latest_version}')
"""
    res = execute(code, snapshot=False)
    mlflow_model = res.values["mlflow_model"]
    assert isinstance(mlflow_model, BaseEstimator)


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
