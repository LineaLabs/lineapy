.. _mlflow:

Using MLflow as Storage Backend to Save ML Models
=================================================

.. include:: ../../../snippets/slack_support.rstinc

By default, LineaPy uses LineaPy to save artifacts for all object types.
However, for users who have access to MLflow, MLflow might be their first choice to save the ML model.
Thus, we enable using MLflow as the backend storage for ML models.

Configure MLflow
----------------

Depend on how our MLflow is configured. We might need to specify ``tracking URI`` and (optional) ``registry URI``in MLflow to start using MLflow. 

.. code:: python

    mlflow.set_tracking_uri('your_mlflow_tracking_uri')
    mlflow.set_registry_uri('your_mlflow_registry_uri')

To let LineaPy be aware of the existence of MLflow, we need to set corresponding config items if we want to use MLflow as the storage backend for ML models.

.. code:: python

    lineapy.options.set('mlflow_tracking_uri','your_mlflow_tracking_uri')
    lineapy.options.set('mlflow_registry_uri','your_mlflow_registry_uri')


.. note::

    For objects not supported by MLflow, it will fall back to using LineaPy as the storage backend as usual.

Set Default Storage Backend for ML Models
-----------------------------------------

Each user might have a different usage pattern for MLflow; some might use it for logging purposes and record all developing models. Some might treat it as a public space and only publish models that meet specific criteria to MLflow. 
In the first case, users want to use MLflow to save artifacts(ML models) by default, and in the second case, users only want to use MLflow to save artifacts when they want.
Thus, we provide an option(``default_ml_models_storage_backend``) to let users decide the default storage backend for ML models when ``mlflow_tracking_uri`` has been set.

Here are behaviors about which storage backend to use for ML models:

.. code:: python

    lineapy.options.set("mlflow_tracking_uri", "databricks")

    lineapy.save(model, 'model') # Use MLflow (if mlflow_tracking_uri is set, default value of default_ml_models_storage_backend is mlflow )
    lineapy.save(model, 'model', storage_backend='mlflow') # Use MLflow
    lineapy.save(model, 'model', storage_backend='lineapy') # Use LineaPy

    lineapy.options.set("default_ml_models_storage_backend", "mlflow")
    lineapy.save(model, 'model') # Use MLflow
    lineapy.save(model, 'model', storage_backend='mlflow') # Use MLflow
    lineapy.save(model, 'model', storage_backend='lineapy') # Use LineaPy

    lineapy.options.set("default_ml_models_storage_backend", "lineapy")
    lineapy.save(model, 'model') # Use LineaPy
    lineapy.save(model, 'model', storage_backend='mlflow') # Use MLflow
    lineapy.save(model, 'model', storage_backend='lineapy') # Use LineaPy

Note that when using MLflow as storage backend, ``lineapy.save`` is wrapping ``mlflow.flavor.log_model`` under the hood.
Users can use all the arguments in ``mlflow.flavor.log_model`` in ``lineapy.save`` as well.
For instance, if we want to specify ``registered_model_name``, we can write the save statement as:

.. code:: python

    lineapy.save(model, name="model", storage_backend="mlflow", registered_model_name="clf")

Retrieve Artifact from Both LineaPy and MLflow
----------------------------------------------

Depend on what users want to do (or be familiar with). 
Users can retrieve the artifact(ML model) from LineaPy and MLflow once users execute ``lineapy.save`` with ``MLflow`` as the storage backend to save the artifact.

.. code:: python

    # LineaPy way
    artifact = lineapy.get('model')
    model = artifact.get_value()

    artifact.get_code() # to slice the code
    lineapy.to_pipeline(['model']) # to create a pipeline 

    # MLflow way
    metadata = artifact.get_metadata()
    client = mlflow.MlflowClient()
    latest_version = client.search_model_versions("name='clf'")[0].version
    mlflow_model = mlflow.sklearn.load_model(f'models:/clf/{latest_version}')    

Which MLflow Model Flavor is Supported
--------------------------------------

Currently, we are supporting following flavors: ``sklearn``, ``xgboost``, ``prophet`` and ``statsmodels``.
We plan to support all MLflow supported model flavors soon.

