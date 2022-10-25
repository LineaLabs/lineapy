"""
Serializer and deserializer for MLflow supported model flavors. Only include 
annotated modules at this time. 

[x] sklearn
[x] prophet
[ ] tensorflow
[ ] keras
[ ] h2o
[ ] gluon
[ ] xgboost
[ ] lightgbm
[ ] catboost
[ ] spacy
[ ] fastai
[ ] statsmodels

"""


mlflow_io = {}

try:
    import mlflow

    try:
        from sklearn.base import BaseEstimator

        mlflow_io["sklearn"] = [
            {
                "class": BaseEstimator,
                "serializer": mlflow.sklearn.log_model,
                "deserializer": mlflow.sklearn.load_model,
            }
        ]
    except Exception:
        pass

    try:
        from prophet import Prophet

        mlflow_io["prophet"] = [
            {
                "class": Prophet,
                "serializer": mlflow.prophet.log_model,
                "deserializer": mlflow.prophet.load_model,
            }
        ]
    except Exception:
        pass

except ImportError:
    pass
