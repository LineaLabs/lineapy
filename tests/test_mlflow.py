from sklearn.base import BaseEstimator


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
