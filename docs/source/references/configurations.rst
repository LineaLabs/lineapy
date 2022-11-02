.. _configurations:

Configuration Reference
=======================

This page contains all the LineaPy configuration items that you can set in `lineapy_config.json`, environment variables, and CLI options when starting LineaPy with ``lineapy command``.
These items are determined by the following order:

- CLI options
- Environment variables
- Configuration file
- Default values

+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| name                                | usage                                 | type    | default                                    | environmental variables                         |
+=====================================+=======================================+=========+============================================+=================================================+
| home_dir                            | LineaPy base folder                   | Path    | `$HOME/.lineapy`                           | `LINEAPY_HOME_DIR`                              |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| artifact_storage_dir                | artifact saving folder                | Path    | `$LINEAPY_HOME_DIR/linea_pickles`          | `LINEAPY_ARTIFACT_STORAGE_DIR`                  |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| database_url                        | LineaPy db connection string          | string  | `sqlite:///$LINEAPY_HOME_DIR/db.sqlite`    | `LINEAPY_DATABASE_URL`                          |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| customized_annotation_folder        | user annotations folder               | Path    | `$LINEAPY_HOME_DIR/customized_annotations` | `LINEAPY_CUSTOMIZED_ANNOTATION_FOLDER`          |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| do_not_track                        | disable user analytics                | boolean | false                                      | `LINEAPY_DO_NOT_TRACK`                          |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| logging_level                       | logging level                         | string  | INFO                                       | `LINEAPY_LOGGING_LEVEL`                         |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| logging_file                        | logging file path                     | Path    | `$LINEAPY_HOME_DIR/lineapy.log`            | `LINEAPY_LOGGING_FILE`                          |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| mlflow_tracking_uri                 | mlflow tracking                       | string  | None                                       | `LINEAPY_MLFLOW_TRACKING_URI`                   |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| mlflow_registry_uri                 | mlflow registry                       | string  | None                                       | `LINEAPY_MLFLOW_REGISTRY_URI`                   |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| default_ml_models_storage_backend   | default storage backend for ml models | string  | mlflow                                     | `LINEAPY_DEFAULT_ML_MODELS_STORAGE_BACKEND`     |
+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+

All LineaPy configuration items follow following naming convention; in configuration file, all variable name should be lower case with underscore, 
all environmental variable name should be upper case with underscore and all CLI options should be lower case.
For instance, all the following options will achieve the same effect of changing to change the LineaPy base folder to ``/lineapy`` and start ipython.

- Adding ``{"home_dir": "/lineapy"}`` in configuration file: and run ``lineapy ipython``
- In environmental variable: ``export LINEAPY_HOME_DIR=/lineapy && lineapy ipython`` 
- In CLI options: ``lineapy --home-dir='/lineapy' ipython``

LineaPy also provides a CLI command to generate the configuration file (as a json file) based on your environmental variables and CLI options for example:

.. code:: bash  
    
    $ lineapy --home-dir='/lineapy' init 

The configuration file shall look like this:

.. code:: json

    {
        "home_dir": "/lineapy",
        "artifact_storage_dir": "/lineapy/linea_pickles",
        "database_url": "sqlite:///lineapy/db.sqlite",
        "customized_annotation_folder": "/lineapy/customized_annotations",
        "do_not_track": false,
        "logging_level": "INFO",
        "logging_file": "/lineapy/lineapy.log"
    }
    


.. note::

    During an interactive session, you can see current configuration items by typing ``lineapy.options``.

    You can also change the lineapy configuration items listed above with ``lineapy.options.set(key, value)``.
    However, it only makes sense to reset the session when the backend database is changed since you cannot retrieve previous information from the new database.
    Thus, the only place to change the LineaPy database is at the beginning of the notebook.

    Note that, you need to make sure whenever you are setting `LINEAPY_DATABASE_URL`, you point to the  `LINEAPY_ARTIFACT_STORAGE_DIR`.
    If not, ``Artifact.get_value`` might return an error that is related cannot find underlying pickle object.



Artifact Storage Location
-------------------------

You can change the artifact storage location by setting the `LINEAPY_ARTIFACT_STORAGE_DIR` environmental variable, 
or other ways mentioned in the above section.

For instance, if you want to use a local directory, e.g., ``~/lineapy/artifact_store``, as your artifact storage location and start IPython you can

- Adding ``{"artifact_storage_dir": "/lineapy/artifact_store"}`` in configuration file: and run ``lineapy ipython``
- In environmental variable: ``export LINEAPY_ARTIFACT_STORAGE_DIR=/lineapy/artifact_store && lineapy ipython`` 
- In CLI options: ``lineapy --artifact-storage-dir='/lineapy/artifact_store' ipython``

or you can start ipython as usual then run ``lineapy.options.set('artifact_storage_dir', '/lineapy/artifact_store')`` at the beginning of the ipython session.

The best way to configure these filesystems is through the ways officially recommended by the cloud storage providers.
For instance, if you want to configure your AWS credential to use an S3 bucket as your artifact storage directory,
you should configure your AWS account just like official using tools(`AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html>`_ or `boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_) you are using to access AWS,
and LineaPy will use the default AWS credentials to access the S3 bucket just like ``pandas`` and ``fsspec``.

Some filesystems might need extra configuration.
In ``pandas``, you can pass these configurations as ``storage_options`` in ``pandas.DataFrame.to_csv(storage_options={some storage options})``,
where the `storage_options` is a filesystem-specific dictionary pass into `fsspec.filesystem <https://filesystem-spec.readthedocs.io/en/latest/api.html>`_ .
In LineaPy, you can use exactly the same ``storage_options`` to handle these extra configuration items, and you can set them with

.. code:: python

    lineapy.options.set('storage_options',{'same storage_options as you use in pandas.io.read_csv'})

or you can put them in the LineaPy configuration files.

Note that, LineaPy does not support configuring these items as LINEAPY environmental variables or CLI options, since passing a dictionary through these two methods are a little bit awkward.
Instead, if you want ot use environmental variables, you should configure it through the official way from the storage provider and ``LineaPy`` should be able to handle these extra configuration items directly.

Note that, which ``storage_options`` items you can set are depends on the filesystem you are using.
In the following section, we will discuss how to set the storage options for S3.

Artifact Backend Storage
------------------------

When an artifact is also an ML model, you can set the ``mlflow_tracking_uri`` and ``mlflow_registry_uri`` (depending on how your MLflow is configured) to use MLflow as the storage backend for ML models; 
i.e., saving the artifact with ``lineapy.save(model, 'model', storage_backend='mlflow')`` to save the artifact(ML model) directly in MLflow but still register in the LineaPy artifact store.

For instance, if you want to use ``databricks`` as your MLflow tracking URI to save your ML models, you can set them with

.. code:: python

    lineapy.options.set('mlflow_tracking_uri', 'databricks')

or you can put it in the LineaPy configuration files, and you can run

.. code:: python

    lineapy.save(model, 'model', storage_backend='mlflow')

to save your artifact(ML model) in MLflow while you can still use it as a typical LineaPy artifact.
If the ``model`` is not supported by MLflow, it will fall back to using the standard LineaPy protocol to save the model as an artifact.

Furthermore, if the ``default_ml_models_storage_backend='mlflow'``(as default when you only set ``mlflow_tracking_uri``), there is no need to specify ``storage_backend='mlflow'`` in the ``lineapy.save`` to save the model in MLflow.
Or you can change to ``default_ml_models_storage_backend='lineapy'``, and save your artifacts(ML models) with LineaPy backend as default and use MLflow when you specify ``storage_backend='mlflow'`` in the ``lineapy.save``.