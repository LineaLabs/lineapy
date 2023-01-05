# Configuring LineaPy

We can configure LineaPy in several different ways:

- Use CLI options when starting LineaPy from the command line
- Set environmental variables
- Create/update configuration file

For instance, the following all achieves the same effect of changing the LineaPy base folder to `/lineapy` and starting `ipython`.

=== "Use CLI option"

    ```bash
    lineapy --home-dir="/lineapy" ipython
    ```

=== "Set environment variable"

    ```bash
    export LINEAPY_HOME_DIR=/lineapy
    lineapy ipython
    ```

=== "Update configuration file"

    Add `{"home_dir": "/lineapy"}` to the configuration file:

    ```json hl_lines="2" title="lineapy_config.json"
    {
        "home_dir": "/lineapy",
        ...
    }
    ```

    and run:

    ```bash
    lineapy ipython
    ```

The value of a configuration item is determined by the following "order of precedence":

1. CLI option
2. Environment variable
3. Configuration file
4. Default value

## Core Configuration Items

| Item                                | Description                           | Type    | Default Value                              | Environment Variable                            |
| ----------------------------------- | ------------------------------------- | ------- | ------------------------------------------ | ----------------------------------------------- |
| home_dir                            | LineaPy base folder                   | Path    | `$HOME/.lineapy`                           | `LINEAPY_HOME_DIR`                              |
| artifact_storage_dir                | artifact saving folder                | Path    | `$LINEAPY_HOME_DIR/linea_pickles`          | `LINEAPY_ARTIFACT_STORAGE_DIR`                  |
| database_url                        | LineaPy db connection string          | string  | `sqlite:///$LINEAPY_HOME_DIR/db.sqlite`    | `LINEAPY_DATABASE_URL`                          |
| customized_annotation_folder        | user annotations folder               | Path    | `$LINEAPY_HOME_DIR/customized_annotations` | `LINEAPY_CUSTOMIZED_ANNOTATION_FOLDER`          |
| do_not_track                        | disable user analytics                | boolean | false                                      | `LINEAPY_DO_NOT_TRACK`                          |
| logging_level                       | logging level                         | string  | INFO                                       | `LINEAPY_LOGGING_LEVEL`                         |
| logging_file                        | logging file path                     | Path    | `$LINEAPY_HOME_DIR/lineapy.log`            | `LINEAPY_LOGGING_FILE`                          |

## Configuration Items for Integration with Other Tools

| Item                                | Description                           | Type    | Default Value                              | Environment Variable                            |
| ----------------------------------- | ------------------------------------- | ------- | ------------------------------------------ | ----------------------------------------------- |
| mlflow_tracking_uri                 | MLflow tracking                       | string  | None                                       | `LINEAPY_MLFLOW_TRACKING_URI`                   |
| mlflow_registry_uri                 | MLflow registry                       | string  | None                                       | `LINEAPY_MLFLOW_REGISTRY_URI`                   |
| default_ml_models_storage_backend   | Default storage backend for ML models | string  | mlflow                                     | `LINEAPY_DEFAULT_ML_MODELS_STORAGE_BACKEND`     |

!!! tip

    LineaPy provides a CLI command to generate the configuration file (as a json file) based on
    existing environmental variables, CLI options, and default values. For example, running:

    ```bash
    $ lineapy --home-dir='/lineapy' init 
    ```

    will generate a configuration file looking as follows:

    ```json hl_lines="2" title="lineapy_config.json"
    {
        "home_dir": "/lineapy",
        "artifact_storage_dir": "/lineapy/linea_pickles",
        "database_url": "sqlite:///lineapy/db.sqlite",
        "customized_annotation_folder": "/lineapy/customized_annotations",
        "do_not_track": false,
        "logging_level": "INFO",
        "logging_file": "/lineapy/lineapy.log"
    }
    ```

!!! info

    In an interactive session, we can type `lineapy.options` to check current configuration item values.
    We can also update configuration items on the fly with `lineapy.options.set(key, value)`,
    but this should be done at the beginning of the session to avoid potential conflicts with prior
    operations in the session.
