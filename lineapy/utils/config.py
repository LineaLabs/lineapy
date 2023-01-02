import datetime
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import fsspec
from fsspec.implementations.local import LocalFileSystem

from lineapy.data.types import ARTIFACT_STORAGE_BACKEND, FilePath
from lineapy.db.utils import create_lineadb_engine

try:
    import mlflow
except ImportError:
    pass

LINEAPY_FOLDER_NAME = ".lineapy"
LOG_FILE_NAME = "lineapy.log"
DEVICE_ID_FILE_NAME = ".devid"
CONFIG_FILE_NAME = "lineapy_config.json"
FILE_PICKLER_BASEDIR = "linea_pickles"
DB_FILE_NAME = "db.sqlite"
CUSTOM_ANNOTATIONS_FOLDER_NAME = "custom-annotations"
CUSTOM_ANNOTATIONS_EXTENSION_NAME = ".annotations.yaml"
DEFAULT_ML_MODELS_STORAGE_BACKEND = ARTIFACT_STORAGE_BACKEND.mlflow.value

logger = logging.getLogger(__name__)


@dataclass
class lineapy_config:
    """LineaPy Configuration

    A dataclass that holds configuration items and sets them as environmental
    variables. All items are initialized with default value. Then replace
    with values in the configuration file (if it is existing in LINEAPY_HOME_DIR,
    use this one, otherwise look for home directory) if available. Then,
    replace with values in environmental variables if possible. Finally, it sets
    all values in environmental variables.

    :param home_dir: home directory of LineaPy (must be local)
    :param database_url: database connection string for LineaPy database
    :param artifact_storage_dir: directory for storing artifacts
    :param customized_annotation_folder: directory for storing customized annotations
    :param do_not_track: opt out or user analytics
    :param logging_level: logging level
    :param logging_file: logging file location (only support local for at this time)
    :param storage_options: a dictionary for artifact storage configuration(same as storage_options in pandas, Dask and fsspec)
    :param mlflow_registry_uri: URI for MLflow registry
    :param mlflow_tracking_uri: URI for MLflow tracking
    :param default_ml_models_storage_backend: Default storage backend if
        at least one of mlflow_tracking_uri or mlflow_registry_uri is not empty
    """

    home_dir: Path
    database_url: Optional[str]
    artifact_storage_dir: Optional[FilePath]
    customized_annotation_folder: Optional[FilePath]
    do_not_track: bool
    logging_level: str
    logging_file: Optional[Path]
    storage_options: Optional[Dict[str, Any]]
    mlflow_registry_uri: Optional[str]
    mlflow_tracking_uri: Optional[str]
    default_ml_models_storage_backend: Optional[ARTIFACT_STORAGE_BACKEND]

    def __init__(
        self,
        home_dir=f"{Path(os.environ.get('HOME','~')).expanduser().resolve()}/{LINEAPY_FOLDER_NAME}",
        database_url=None,
        artifact_storage_dir=None,
        customized_annotation_folder=None,
        do_not_track=False,
        logging_level="INFO",
        logging_file=None,
        storage_options=None,
        mlflow_registry_uri=None,
        mlflow_tracking_uri=None,
        default_ml_models_storage_backend=None,
    ):
        if logging_level.isdigit():
            logging_level = logging._levelToName[int(logging_level)]

        self.home_dir = Path(home_dir).expanduser()
        self.storage_options = storage_options
        self.database_url = database_url
        self.artifact_storage_dir = artifact_storage_dir
        self.customized_annotation_folder = customized_annotation_folder
        self.do_not_track = do_not_track
        self.logging_level = logging_level
        self.logging_file = logging_file
        self.dev_id = None
        self.mlflow_registry_uri = mlflow_registry_uri
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.default_ml_models_storage_backend = (
            default_ml_models_storage_backend
        )

        # config file
        config_file_path = Path(
            os.environ.get(
                "LINEAPY_HOME_DIR",
                f"{Path(os.environ.get('HOME','~')).expanduser().resolve()}/{LINEAPY_FOLDER_NAME}",
            )
        ).joinpath(CONFIG_FILE_NAME)
        if config_file_path.exists():
            with open(config_file_path, "r") as f:
                _read_config = json.load(f)
        else:
            config_file_path = (
                Path(os.environ.get("HOME", "~"))
                .expanduser()
                .resolve()
                .joinpath(CONFIG_FILE_NAME)
            )
            if config_file_path.exists():
                with open(config_file_path, "r") as f:
                    _read_config = json.load(f)
            else:
                _read_config = {}

        # env vars
        for key, default_value in self.__dict__.items():
            env_var_value = os.environ.get(f"LINEAPY_{key.upper()}")
            config_value = _read_config.get(key, None)
            # set config value based on environ -> config  -> default
            if env_var_value is not None:
                # special logic to handle serialization of storage options
                if key == "storage_options":
                    env_var_value = json.loads(env_var_value)
                self.set(key, env_var_value, verbose=False)
            elif config_value is not None:
                self.set(key, config_value, verbose=False)
            elif default_value is not None:
                self.set(key, default_value, verbose=False)

        self._set_defaults()

    def get(self, key: str) -> Any:
        """Get LineaPy config field"""
        if key in self.__dict__.keys():
            # fill empty default_ml_models_storage_backend if
            # mlflow_registry_uri or mlflow_tracking_uri is set
            if (
                key == "default_ml_models_storage_backend"
                and (getattr(self, key) is None)
                and (
                    (getattr(self, "mlflow_tracking_uri") is not None)
                    or (getattr(self, "mlflow_registry_uri") is not None)
                )
            ):
                self.set(
                    "default_ml_models_storage_backend",
                    DEFAULT_ML_MODELS_STORAGE_BACKEND,
                )
            return getattr(self, key)
        else:
            logger.error(key, "is not a lineapy config item")
            raise NotImplementedError

    def set(self, key: str, value: Any, verbose=True) -> None:
        """Set LineaPy config field"""
        if key not in self.__dict__.keys():
            logger.error(key, "is not a lineapy config item")
            raise NotImplementedError
        else:
            if key == "database_url":
                try:
                    new_db = create_lineadb_engine(value)
                    self.__dict__[key] = value
                    os.environ[f"LINEAPY_{key.upper()}"] = str(value)
                    if verbose:
                        logger.warning(
                            f"LineaPy database is changed to {value}, resetting notebook session in next cell"
                        )
                except Exception as e:
                    logger.warning(
                        f"LineaPy cannot connect to {value}. Is this a valid database connection string? Ignore setting LineaPy database."
                    )
            else:
                self.__dict__[key] = value
                # special logic to handle serialization of storage options
                if key == "storage_options":
                    os.environ[f"LINEAPY_{key.upper()}"] = json.dumps(value)
                else:
                    os.environ[f"LINEAPY_{key.upper()}"] = str(value)

            if key == "mlflow_registry_uri":
                if "mlflow" in sys.modules:
                    mlflow.set_registry_uri(value)
                else:
                    raise ModuleNotFoundError("mlflow is not installed")

            if key == "mlflow_tracking_uri":
                if "mlflow" in sys.modules:
                    mlflow.set_tracking_uri(value)
                else:
                    raise ModuleNotFoundError("mlflow is not installed")

            # Send a heartbeat to artifact_storage_dir
            if key == "artifact_storage_dir":
                storage_options = (
                    {}
                    if self.storage_options is None
                    else self.storage_options
                )
                with fsspec.open(
                    str(self.safe_get("artifact_storage_dir")).rstrip("/")
                    + "/heartbeat",
                    "w",
                    **storage_options,
                ) as f:
                    f.write(
                        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    )

    def _set_defaults(self):
        """Fill empty configuration items"""
        self.safe_get("logging_file")
        self.safe_get("database_url")
        self.safe_get("artifact_storage_dir")
        self.safe_get("customized_annotation_folder")

    def safe_get(self, name) -> FilePath:
        def safe_get_folder(name) -> FilePath:
            """Return folder as FilePath
            Create the folder if it doesn't exist"""

            if isinstance(self.__dict__[name], Path) or isinstance(
                fsspec.core.url_to_fs(self.__dict__[name])[0],
                LocalFileSystem,
            ):
                local_path = Path(self.__dict__[name]).resolve()
                if not local_path.exists():
                    logger.warning(
                        f"Folder {local_path.as_posix()} does not exist. Creating a new one."
                    )
                    local_path.mkdir(parents=True, exist_ok=True)
                return local_path
            return self.__dict__[name]

        # Return logging_file path, use LINEAPY_HOME_DIR/LOG_FILE_NAME if empty
        if name == "logging_file":
            if self.logging_file is None:
                logging_file = Path(safe_get_folder("home_dir")).joinpath(
                    LOG_FILE_NAME
                )
                self.set("logging_file", logging_file, verbose=False)
            else:
                logging_file = Path(str(self.logging_file))

            return logging_file

        # Return LINEAPY_DATABASE_url, use sqlite:///{LINEAPY_HOME_DIR}/{DB_FILE_NAME} if empty
        elif name == "database_url":
            if self.database_url is None:
                self.set(
                    "database_url",
                    f"sqlite:///{Path(safe_get_folder('home_dir')).as_posix()}/{DB_FILE_NAME}",
                    verbose=False,
                )
            return str(self.database_url)

        # Return LINEAPY_ARTIFACT_STORAGE_DIR, use LINEAPY_HOME_DIR/FILE_PICKLER_BASEDIR if empty
        elif name == "artifact_storage_dir":
            if self.artifact_storage_dir is None:
                self.set(
                    "artifact_storage_dir",
                    Path(safe_get_folder("home_dir")).joinpath(
                        FILE_PICKLER_BASEDIR
                    ),
                    verbose=False,
                )

            return safe_get_folder("artifact_storage_dir")

        # Return LINEAPY_CUSTOMIZED_ANNOTATION_FOLDER, use LINEAPY_HOME_DIR/CUSTOM_ANNOTATIONS_FOLDER_NAME if empty
        elif name == "customized_annotation_folder":
            if self.customized_annotation_folder is None:
                self.set(
                    "customized_annotation_folder",
                    Path(safe_get_folder("home_dir")).joinpath(
                        CUSTOM_ANNOTATIONS_FOLDER_NAME
                    ),
                    verbose=False,
                )
            return safe_get_folder("customized_annotation_folder")

        elif name == "dev_id":
            if self.dev_id is None:
                dev_id_file = Path(safe_get_folder("home_dir")).joinpath(
                    DEVICE_ID_FILE_NAME
                )
                self.set(
                    "dev_id",
                    dev_id_file,
                    verbose=False,
                )
            else:
                dev_id_file = logging_file = Path(str(self.dev_id))
            return dev_id_file
        else:
            return self.get(name)


options = lineapy_config()
