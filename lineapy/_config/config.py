import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import toml

LINEAPY_FOLDER_NAME = ".lineapy"
LOG_FILE_NAME = "lineapy.log"
CONFIG_FILE_NAME = "lineapy_config.toml"
FILE_PICKLER_BASEDIR = "linea_pickles"
DB_FILE_NAME = "db.sqlite"

logger = logging.getLogger(__name__)


@dataclass
class LineapyConfig:
    home_dir: Path
    artifact_database_connection_string: Optional[str]
    artifact_storage_backend: str
    artifact_storage_dir: Optional[Path]
    customized_annotation_folder: Optional[Path]
    do_not_track: bool
    logging_level: str
    logging_file: Optional[Path]
    # artifact_aws_s3_bucket : str
    # artifact_aws_s3_bucket_prefix : str
    # ipython_dir : Path

    def __init__(
        self,
        home_dir=f"{os.environ.get('HOME','~')}/{LINEAPY_FOLDER_NAME}",
        artifact_database_connection_string=None,
        artifact_storage_backend="local",
        artifact_storage_dir=None,
        customized_annotation_folder=None,
        do_not_track=False,
        logging_level="INFO",
        logging_file=None,
        # artifact_aws_s3_bucket = None,
        # artifact_aws_s3_bucket_prefix = None,
        # ipython_dir = None
    ):
        self.home_dir = home_dir
        self.artifact_database_connection_string = (
            artifact_database_connection_string
        )
        self.artifact_storage_backend = artifact_storage_backend
        self.artifact_storage_dir = artifact_storage_dir
        self.customized_annotation_folder = customized_annotation_folder
        self.do_not_track = do_not_track
        self.logging_level = logging_level
        self.logging_file = logging_file
        # self.artifact_aws_s3_bucket = artifact_aws_s3_bucket
        # self.artifact_aws_s3_bucket_prefix = artifact_aws_s3_bucket_prefix
        # self.ipython_dir = ipython_dir

        # config file
        config_file_path = Path(
            os.environ.get(
                "LINEAPY_HOME_DIR",
                f"{os.environ.get('HOME','~')}/{LINEAPY_FOLDER_NAME}",
            )
        ).joinpath(CONFIG_FILE_NAME)
        if config_file_path.exists():
            _read_config = toml.load(config_file_path)
        else:
            config_file_path = Path(os.environ.get("HOME", "~")).joinpath(
                CONFIG_FILE_NAME
            )
            if config_file_path.exists():
                _read_config = toml.load(config_file_path)
            else:
                _read_config = {}

        for key, value in _read_config.items():
            if key in self.__dict__.keys():
                self.set(key, value)

        # env vars
        for var_name in self.__dict__.keys():
            env_var_value = os.environ.get(f"LINEAPY_{var_name.upper()}")
            if env_var_value is not None:
                self.set(var_name, env_var_value)

    def get(self, key: str) -> Any:
        if key in self.__dict__.keys():
            return getattr(self, key)
        else:
            logger.error(key, "is not a lineapy config item")
            raise Exception  # Unimplemented

    def set(self, key, value) -> None:
        logger.warning(
            "Modify lineapy config during session might cause some unexpected behaviors"
        )
        if key not in self.__dict__.keys():
            logger.error(key, "is not a lineapy config item")
            raise Exception  # Unimplemented
        else:
            self.__dict__[key] = value
            os.environ[f"LINEAPY_{key.upper()}"] = str(value)

    # def reset(self)

    def get_artifact_storage_dir(self) -> Path:
        """
        If artifact_storage_dir is set, return it; otherwise use home_dir/FILE_PICKLER_BASEDIR
        """
        artifact_storage_dir = self.artifact_storage_dir
        if artifact_storage_dir is None:
            artifact_storage_dir = self._save_get_home_dir().joinpath(
                FILE_PICKLER_BASEDIR
            )

        if not artifact_storage_dir.exists():
            logger.warning(
                f"No {artifact_storage_dir.name} folder found. Creating a new folder in {artifact_storage_dir.parent.as_posix()} directory."
            )
            artifact_storage_dir.mkdir(parents=False, exist_ok=True)
        return artifact_storage_dir

    def get_artifact_database_connection_string(self) -> str:
        """
        If artifact_database_connection_string is set, return it; otherwise use sqlite:///home_dir/DB_FILE_NAME
        """
        artifact_database_connection_string = (
            self.artifact_database_connection_string
        )
        if artifact_database_connection_string is None:
            artifact_database_connection_string = (
                f"sqlite:///{self._save_get_home_dir()}/{DB_FILE_NAME}"
            )
        return artifact_database_connection_string

    def get_logging_file(self) -> Path:
        logging_file = self.logging_file
        if logging_file is None:
            logging_file = self._save_get_home_dir().joinpath(LOG_FILE_NAME)
        return logging_file

    def _save_get_home_dir(self) -> Path:
        if not Path(self.home_dir).exists():
            Path(self.home_dir).mkdir()
        return Path(self.home_dir)


options = LineapyConfig()
