Overview
========

.. include:: /snippets/slack_support.rstinc

This page contains all the LineaPy configuration items that you can set in ``lineapy_config.json``, environment variables, and CLI options when starting LineaPy with ``lineapy command``.
These items are determined by the following order:

- CLI options
- Environment variables
- Configuration file
- Default values

* Core LineaPy configuration items

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

* Configuration item for integration with other tools

+-------------------------------------+---------------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| name                                | usage                                 | type    | default                                    | environmental variables                         |
+=====================================+=======================================+=========+============================================+=================================================+
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

.. include:: /snippets/docs_feedback.rstinc
