.. _configurations:

Configuration Reference
=======================

This page contains all the LineaPy configuration items that you can set in `lineapy_config.json`, environment variables, and CLI options when starting LineaPy with ``lineapy command``.
These items are determined by the following order:

- CLI options
- Environment variables
- Configuration file
- Default values

+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| name                                | usage                         | type    | default                                    | environmental variables                         |
+=====================================+===============================+=========+============================================+=================================================+
| home_dir                            | LineaPy base folder           | Path    | `$HOME/.lineapy`                           | `LINEAPY_HOME_DIR`                              |
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| artifact_storage_dir                | artifact saving folder        | Path    | `$LINEAPY_HOME_DIR/linea_pickles`          | `LINEAPY_ARTIFACT_STORAGE_DIR`                  |
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| database_connection_string          | LineaPy db connection string  | string  | `sqlite:///$LINEAPY_HOME_DIR/db.sqlite`    | `LINEAPY_DATABASE_CONNECTION_STRING`            |
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| customized_annotation_folder        | user annotations folder       | Path    | `$LINEAPY_HOME_DIR/customized_annotations` | `LINEAPY_CUSTOMIZED_ANNOTATION_FOLDER`          |
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| do_not_track                        | disable user analytics        | boolean | false                                      | `LINEAPY_DO_NOT_TRACK`                          |
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| logging_level                       | logging level                 | string  | INFO                                       | `LINEAPY_LOGGING_LEVEL`                         |
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+
| logging_file                        | logging file path             | Path    | `$LINEAPY_HOME_DIR/lineapy.log`            | `LINEAPY_LOGGING_FILE`                          | 
+-------------------------------------+-------------------------------+---------+--------------------------------------------+-------------------------------------------------+

All LineaPy configuration items follow following naming convention; in configuration file, all variable name should be lower case with underscore, 
all environmental variable name should be upper case with underscore and all CLI options should be lower case.
For instance, all the following options will achieve the same effect of changing to change the LineaPy base folder to ``/lineapy`` and start ipython.

- Adding ``{"home_dir": "/lineapy"}`` in configuration file: and run ``lineapy ipython``
- In environmental variable: ``export LINEAPY_HOME_DIR=/lineapy && lineapy ipython`` 
- In CLI options: ``lineapy --home-dir='/lineapy' ipython``

LineaPy also provides a CLI command to generate the configuration file (as a json file) based on your environmental variables and CLI options for example:

.. code:: bash  
    
    $ lineapy --home-dir='/lineapy' init 


Interactive Mode
----------------

During an interactive session, you can change the lineapy configuration items listed above with ``lineapy.options.set(key, value)``.

However, if you change the LineaPy database(with `LINEAPY_DATABASE_CONNECTION_STRING`), LineaPy will reset your ENTIRE notebook session since LineaPy is saving node information eagerly to the backend database. 
It only makessense to reset the session when the backend database is changed since you cannot retrieve previous information from the new database.
Thus, the only place to change the LineaPy database is at the beginning of the notebook.

Note that, you need to make sure you are setting `LINEAPY_ARTIFACT_STORAGE_DIR` correctly whenever you set `LINEAPY_DATABASE_CONNECTION_STRING`.
If not, `Artifact.get_value` might return an error that is related cannot find underlying pickle object.