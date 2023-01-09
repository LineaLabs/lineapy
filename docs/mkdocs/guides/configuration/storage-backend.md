# Changing Storage Backend

Out of the box, LineaPy is the default storage backend for all artifacts.
For certain storage backends in use (e.g., storing model artifacts in MLflow),
saving one more copy of the same artifact into LineaPy causes sync issue between the two systems.
Thus, LineaPy supports using different storage backends for certain data types (e.g., ML models).
This support is essential for users to leverage functionalities from both LineaPy
and other familiar toolkit (e.g., MLflow).

!!! note

    Storage backend refers to the overall system handling storage and should be distinguished from
    specific storage locations such as Amazon S3. For instance, LineaPy is a storage backend
    that can use different storage locations.

## Saving ML Models to MLflow Backend

By default, LineaPy uses LineaPy to save artifacts for all object types.
However, for users who have access to MLflow, MLflow might be their first choice to save the ML model.
Thus, we enable using MLflow as the backend storage for ML models.

!!! info

    Supported model flavors include `sklearn`, `xgboost`, `prophet`, and `statsmodels` at the moment.
    The list is planned to be expanded to cover all MLflow-supported model flavors.

!!! info

    For objects not supported by MLflow, storage will fall back to the LineaPy backend as usual.

### Configuring MLflow

Depending on how our MLflow is configured, we might need to specify `tracking URI` and
(optional) `registry URI` in MLflow to start using MLflow. 

```python
mlflow.set_tracking_uri('your_mlflow_tracking_uri')
mlflow.set_registry_uri('your_mlflow_registry_uri')
```

To let LineaPy be aware of the existence of MLflow, we need to set corresponding config items
if we want to use MLflow as the storage backend for ML models.

```python
lineapy.options.set('mlflow_tracking_uri','your_mlflow_tracking_uri')
lineapy.options.set('mlflow_registry_uri','your_mlflow_registry_uri')
```

### Setting Default Storage Backend for ML Models

Each user might have a different usage pattern for MLflow; some might use it for logging purposes and
record all developing models. Some might treat it as a public space and only publish models that meet
specific criteria to MLflow. In the first case, users want to use MLflow to save artifacts(ML models)
by default, and in the second case, users only want to use MLflow to save artifacts when they want.
Thus, we provide an option (`default_ml_models_storage_backend`) to let users decide the default storage backend
for ML models when `mlflow_tracking_uri` has been set.

Here are behaviors about which storage backend to use for ML models:

* Only set `mlflow_tracking_uri` but not `default_ml_models_storage_backend`

```python
lineapy.options.set("mlflow_tracking_uri", "databricks")

lineapy.save(model, "model") # Use MLflow (if mlflow_tracking_uri is set, default value of default_ml_models_storage_backend is mlflow)
lineapy.save(model, "model", storage_backend="mlflow") # Use MLflow
lineapy.save(model, "model", storage_backend="lineapy") # Use LineaPy
```

* Set `mlflow_tracking_uri` and `default_ml_models_storage_backend=="mlflow"`

```python
lineapy.options.set("mlflow_tracking_uri", "databricks")
lineapy.options.set("default_ml_models_storage_backend", "mlflow")

lineapy.save(model, "model") # Use MLflow
lineapy.save(model, "model", storage_backend="mlflow") # Use MLflow
lineapy.save(model, "model", storage_backend="lineapy") # Use LineaPy
```

* Set `mlflow_tracking_uri` and `default_ml_models_storage_backend=="lineapy"`

```python
lineapy.options.set("mlflow_tracking_uri", "databricks")
lineapy.options.set("default_ml_models_storage_backend", "lineapy")

lineapy.save(model, "model") # Use LineaPy
lineapy.save(model, "model", storage_backend="mlflow") # Use MLflow
lineapy.save(model, "model", storage_backend="lineapy") # Use LineaPy
```

Note that when using MLflow as storage backend, `lineapy.save()` is wrapping `mlflow.flavor.log_model`
under the hood. Users can use all the arguments in `mlflow.flavor.log_model` in `lineapy.save()` as well.
For instance, if we want to specify `registered_model_name`, we can write the save statement as:

```python
lineapy.save(model, name="model", storage_backend="mlflow", registered_model_name="clf")
```

### Retrieving Artifact from Both LineaPy and MLflow

Depending on what users want to do (or be familiar with), users can retrieve the same artifact (ML model)
from LineaPy API and MLflow API once users execute `lineapy.save()` with `mlflow` as the storage backend
to save the artifact.

* Retrieve artifact (model) with LineaPy API

```python
artifact = lineapy.get("model")
lineapy_model = artifact.get_value()
```

* Retrieve artifact (model) with MLflow API

```python
client = mlflow.MlflowClient()
latest_version = client.search_model_versions("name='clf'")[0].version
# This is exactly the same object as `lineapy_model` in previous session
mlflow_model = mlflow.sklearn.load_model(f'models:/clf/{latest_version}')    
```
