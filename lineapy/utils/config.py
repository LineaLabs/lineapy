import json
import logging
import os
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any, Optional

LINEAPY_FOLDER_NAME = ".lineapy"
LOG_FILE_NAME = "lineapy.log"
CONFIG_FILE_NAME = "lineapy_config.json"
FILE_PICKLER_BASEDIR = "linea_pickles"
DB_FILE_NAME = "db.sqlite"
CUSTOM_ANNOTATIONS_FOLDER_NAME = "custom-annotations"
CUSTOM_ANNOTATIONS_EXTENSION_NAME = ".annotations.yaml"

logger = logging.getLogger(__name__)


@dataclass
class LineapyConfig:
    """LineaPy Configuration

    A dataclass that holds configuration items and sets them as environmental
    variables. All items are initialized with default value. Then replace
    with values in the configuration file (if it is existing in LINEAPY_HOME_DIR,
    use this one, otherwise look for home directory) if available. Then,
    replace with values in environmental variables if possible. Finally, it sets
    all values in environmental variables.

    """

    home_dir: Path
    database_connection_string: Optional[str]
    # artifact_storage_backend: str
    artifact_storage_dir: Optional[Path]
    customized_annotation_folder: Optional[Path]
    do_not_track: bool
    logging_level: str
    logging_file: Optional[PathLike]
    # artifact_aws_s3_bucket : str
    # artifact_aws_s3_bucket_prefix : str
    # ipython_dir : Path

    def __init__(
        self,
        home_dir=f"{os.environ.get('HOME','~')}/{LINEAPY_FOLDER_NAME}",
        database_connection_string=None,
        # artifact_storage_backend="local",
        artifact_storage_dir=None,
        customized_annotation_folder=None,
        do_not_track=False,
        logging_level="INFO",
        logging_file=None,
        # artifact_aws_s3_bucket = None,
        # artifact_aws_s3_bucket_prefix = None,
    ):
        self.home_dir = home_dir
        self.database_connection_string = database_connection_string
        # self.artifact_storage_backend = artifact_storage_backend
        self.artifact_storage_dir = artifact_storage_dir
        self.customized_annotation_folder = customized_annotation_folder
        self.do_not_track = do_not_track
        self.logging_level = logging_level
        self.logging_file = logging_file
        # self.artifact_aws_s3_bucket = artifact_aws_s3_bucket
        # self.artifact_aws_s3_bucket_prefix = artifact_aws_s3_bucket_prefix

        # config file
        config_file_path = Path(
            os.environ.get(
                "LINEAPY_HOME_DIR",
                f"{os.environ.get('HOME','~')}/{LINEAPY_FOLDER_NAME}",
            )
        ).joinpath(CONFIG_FILE_NAME)
        if config_file_path.exists():
            with open(config_file_path, "r") as f:
                _read_config = json.load(f)
        else:
            config_file_path = Path(os.environ.get("HOME", "~")).joinpath(
                CONFIG_FILE_NAME
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
                self.set(key, env_var_value)
            elif config_value is not None:
                self.set(key, config_value)
            elif default_value is not None:
                self.set(key, default_value)

    def get(self, key: str) -> Any:
        """Get LineaPy config field"""
        if key in self.__dict__.keys():
            return getattr(self, key)
        else:
            logger.error(key, "is not a lineapy config item")
            raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        """Set LineaPy config field"""
        if key not in self.__dict__.keys():
            logger.error(key, "is not a lineapy config item")
            raise NotImplementedError
        else:
            self.__dict__[key] = value
            os.environ[f"LINEAPY_{key.upper()}"] = str(value)

    def _set_defaults(self):
        """Fill empty configuration items"""
        self._safe_get_logging_file()
        self._safe_get_database_connection_string()
        self._safe_get_artifact_storage_dir()
        self._safe_get_customized_annotation_folder()

    def _safe_get_folder(self, name) -> Path:
        """Return folder as pathlib.Path
        Create the folder if it doesn't exist"""
        if not Path(self.__dict__[name]).exists():
            logger.warning(
                f"Folder {Path(self.__dict__[name]).as_posix()} does not exist. Creating a new one."
            )
            Path(self.__dict__[name]).mkdir(parents=True, exist_ok=True)
        return Path(self.__dict__[name])

    def _safe_get_logging_file(self) -> Path:
        """Return logging_file path
        Use LINEAPY_HOME_DIR/LOG_FILE_NAME if empty"""
        if self.logging_file is None:
            self.set(
                "logging_file",
                self._safe_get_folder("home_dir").joinpath(LOG_FILE_NAME),
            )
        return Path(str(self.logging_file))

    def _safe_get_database_connection_string(self) -> str:
        """Return LINEAPY_DATABASE_CONNECTION_STRING
        Use sqlite:///{LINEAPY_HOME_DIR}/{DB_FILE_NAME} if empty"""
        if self.database_connection_string is None:
            self.set(
                "database_connection_string",
                f"sqlite:///{self._safe_get_folder('home_dir')}/{DB_FILE_NAME}",
            )
        return str(self.database_connection_string)

    def _safe_get_artifact_storage_dir(self) -> Path:
        """Return LINEAPY_ARTIFACT_STORAGE_DIR
        Use LINEAPY_HOME_DIR/FILE_PICKLER_BASEDIR if empty"""
        if self.artifact_storage_dir is None:
            self.set(
                "artifact_storage_dir",
                self._safe_get_folder("home_dir").joinpath(
                    FILE_PICKLER_BASEDIR
                ),
            )
        return self._safe_get_folder("artifact_storage_dir")

    def _safe_get_customized_annotation_folder(self) -> Path:
        """Return LINEAPY_CUSTOMIZED_ANNOTATION_FOLDER
        Use LINEAPY_HOME_DIR/CUSTOM_ANNOTATIONS_FOLDER_NAME if empty"""
        if self.customized_annotation_folder is None:
            self.set(
                "customized_annotation_folder",
                self._safe_get_folder("home_dir").joinpath(
                    CUSTOM_ANNOTATIONS_FOLDER_NAME
                ),
            )
        return self._safe_get_folder("customized_annotation_folder")


options = LineapyConfig()
