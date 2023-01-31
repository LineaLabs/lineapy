"""
Serializer and deserializer for MLflow supported model flavors. Only include 
annotated modules at this time. 

- [x] sklearn
- [x] prophet
- [ ] tensorflow (need update current annotation)
- [ ] keras (need update current annotation)
- [ ] h2o
- [ ] gluon
- [x] xgboost
- [ ] lightgbm
- [ ] catboost
- [ ] spacy
- [ ] fastai
- [x] statsmodels

"""

import logging
import sys
from inspect import getmodule
from typing import Any, Optional

from lineapy.data.types import MLflowArtifactInfo
from lineapy.utils.config import options
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()

mlflow_io = {}
"""
This dictionary holds information about how to serialize and deserialize for 
each MLflow supported model flavors. Each individual key is a module name; 
i.e., MLflow supported flavor, ``sklearn`` for instance. Each value is a 
dictionary with following three keys:

1. class: list of object class with the module that can be log/save in MLflow 
2. serializer: the method in MLflow to log the model flavor
3. deserializer is the method in MLflow to retrieve the model
"""

try:
    import mlflow

    try:
        from sklearn.base import BaseEstimator

        mlflow_io["sklearn"] = {
            "class": [BaseEstimator],
            "serializer": mlflow.sklearn.log_model,
            "deserializer": mlflow.sklearn.load_model,
        }
    except Exception:
        pass

    try:
        from prophet import Prophet

        mlflow_io["prophet"] = {
            "class": [Prophet],
            "serializer": mlflow.prophet.log_model,
            "deserializer": mlflow.prophet.load_model,
        }
    except Exception:
        pass

    try:
        from xgboost.core import Booster

        mlflow_io["xgboost"] = {
            "class": [Booster],
            "serializer": mlflow.xgboost.log_model,
            "deserializer": mlflow.xgboost.load_model,
        }
    except Exception:
        pass

    try:
        from statsmodels.base.wrapper import ResultsWrapper

        mlflow_io["statsmodels"] = {
            "class": [ResultsWrapper],
            "serializer": mlflow.statsmodels.log_model,
            "deserializer": mlflow.statsmodels.load_model,
        }
    except Exception:
        pass

except ImportError:
    pass


def try_write_to_mlflow(value: Any, name: str, **kwargs) -> Optional[Any]:
    """
    Try to save artifact with MLflow. If success return mlflow ModelInfo,
    return None if fail.

    Parameters
    ----------
    value: Any
        value(ML model) to save with mlflow
    name: str
        artifact_path and registered_model_name used in
        `mlflow.sklearn.log_model` or equivalent flavors
    **kwargs:
        args to pass into `mlflow.sklearn.log_model` or equivalent flavors

    Returns
    -------
    Optional[Any]
        return a ModelInfo(MLflow model metadata) if successfully save with
        mlflow; otherwise None. Note that, using Any not ModelInfo here in
        case mlflow is not installed and cause error when loading lineapy

    """

    logger.info("Trying to save the object to MLflow.")

    # Check mlflow is installed, if not raise error
    if "mlflow" not in sys.modules:
        msg = (
            "module 'mlflow' is not installed;"
            + " please install it with 'pip install lineapy[mlflow]'"
        )
        raise ModuleNotFoundError(msg)
    mlflow.set_tracking_uri(options.get("mlflow_tracking_uri"))

    # Check value is from a module supported by mlflow
    full_module_name = getmodule(value)
    if full_module_name is not None:
        root_module_name = full_module_name.__name__.split(".")[0]
        if root_module_name in mlflow_io.keys():
            flavor_io = mlflow_io[root_module_name]
            # Check value is the right class type for the module supported by mlflow
            if any(
                [
                    isinstance(value, target_class)
                    for target_class in flavor_io["class"]
                ]
            ):
                kwargs["registered_model_name"] = kwargs.get(
                    "registered_model_name", name
                )
                kwargs["artifact_path"] = kwargs.get("artifact_path", name)
                # This is where save to MLflow happen
                model_info = flavor_io["serializer"](value, **kwargs)
                return model_info

    logger.info(
        f"LineaPy is currently not supporting saving {type(value)} to MLflow."
    )
    return None


def read_mlflow(mlflow_metadata: MLflowArtifactInfo) -> Any:
    """
    Read model from MLflow artifact store

    In case the saved tracking_uri or the registry_uri is different from
    lineapy configs(i.e., multiple MLflow backends), we recored current
    lineapy related mlflow configs for tracking/registry and set
    tracking/registry based on metadata to load the model and reset back
    to the original configs.
    """

    current_mlflow_tracking_uri = options.get("mlflow_tracking_uri")
    current_mlflow_registry_uri = options.get("mlflow_registry_uri")
    mlflow.set_tracking_uri(mlflow_metadata.tracking_uri)
    mlflow.set_registry_uri(mlflow_metadata.registry_uri)

    assert isinstance(mlflow_metadata.model_flavor, str)
    value = mlflow_io[mlflow_metadata.model_flavor]["deserializer"](
        mlflow_metadata.model_uri
    )

    mlflow.set_tracking_uri(current_mlflow_tracking_uri)
    mlflow.set_registry_uri(current_mlflow_registry_uri)
    return value
