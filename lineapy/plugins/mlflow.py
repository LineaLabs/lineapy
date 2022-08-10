import mlflow
from sklearn.base import BaseEstimator

from lineapy.utils.config import options


def log_model(model, artifact_path, **kwargs) -> None:
    if options.get("mlflow_tracking_uri") is not None:
        mlflow.set_tracking_uri("sqlite:///mlruns.db")
        if isinstance(model, BaseEstimator):
            mlflow.sklearn.log_model(
                model,
                artifact_path,
                registered_model_name=artifact_path,
                **kwargs
            )
