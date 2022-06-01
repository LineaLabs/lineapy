import json
import logging
import os
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union

from lineapy.db.utils import create_lineadb_engine

LINEAPY_FOLDER_NAME = ".lineapy"
LOG_FILE_NAME = "lineapy.log"
CONFIG_FILE_NAME = "lineapy_config.json"
FILE_PICKLER_BASEDIR = "linea_pickles"
DB_FILE_NAME = "db.sqlite"
CUSTOM_ANNOTATIONS_FOLDER_NAME = "custom-annotations"
CUSTOM_ANNOTATIONS_EXTENSION_NAME = ".annotations.yaml"

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

    """

    home_dir: Path
    database_url: Optional[str]
    artifact_storage_dir: Optional[Path]
    customized_annotation_folder: Optional[Path]
    do_not_track: bool
    logging_level: str
    logging_file: Optional[PathLike]

    def __init__(
        self,
        home_dir=f"{os.environ.get('HOME','~')}/{LINEAPY_FOLDER_NAME}",
        database_url=None,
        artifact_storage_dir=None,
        customized_annotation_folder=None,
        do_not_track=False,
        logging_level="INFO",
        logging_file=None,
    ):
        if logging_level.isdigit():
            logging_level = logging._levelToName[int(logging_level)]

        self.home_dir = home_dir
        self.database_url = database_url
        self.artifact_storage_dir = artifact_storage_dir
        self.customized_annotation_folder = customized_annotation_folder
        self.do_not_track = do_not_track
        self.logging_level = logging_level
        self.logging_file = logging_file

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
                self.set(key, env_var_value, verbose=False)
            elif config_value is not None:
                self.set(key, config_value, verbose=False)
            elif default_value is not None:
                self.set(key, default_value, verbose=False)

    def get(self, key: str) -> Any:
        """Get LineaPy config field"""
        if key in self.__dict__.keys():
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
                os.environ[f"LINEAPY_{key.upper()}"] = str(value)

    def _set_defaults(self):
        """Fill empty configuration items"""
        self.safe_get("logging_file")
        self.safe_get("database_url")
        self.safe_get("artifact_storage_dir")
        self.safe_get("customized_annotation_folder")

    def safe_get(self, name) -> Union[Path, str]:
        def safe_get_folder(name) -> Path:
            """Return folder as pathlib.Path
            Create the folder if it doesn't exist"""
            if not Path(self.__dict__[name]).exists():
                logger.warning(
                    f"Folder {Path(self.__dict__[name]).as_posix()} does not exist. Creating a new one."
                )
                Path(self.__dict__[name]).mkdir(parents=True, exist_ok=True)
            return Path(self.__dict__[name])

        # Return logging_file path, use LINEAPY_HOME_DIR/LOG_FILE_NAME if empty
        if name == "logging_file":
            if self.logging_file is None:
                self.set(
                    "logging_file",
                    safe_get_folder("home_dir").joinpath(LOG_FILE_NAME),
                    verbose=False,
                )
            return Path(str(self.logging_file))

        # Return LINEAPY_DATABASE_url, use sqlite:///{LINEAPY_HOME_DIR}/{DB_FILE_NAME} if empty
        elif name == "database_url":
            if self.database_url is None:
                self.set(
                    "database_url",
                    f"sqlite:///{safe_get_folder('home_dir')}/{DB_FILE_NAME}",
                    verbose=False,
                )
            return str(self.database_url)

        # Return LINEAPY_ARTIFACT_STORAGE_DIR, use LINEAPY_HOME_DIR/FILE_PICKLER_BASEDIR if empty
        elif name == "artifact_storage_dir":
            if self.artifact_storage_dir is None:
                self.set(
                    "artifact_storage_dir",
                    safe_get_folder("home_dir").joinpath(FILE_PICKLER_BASEDIR),
                    verbose=False,
                )
            return safe_get_folder("artifact_storage_dir")

        # Return LINEAPY_CUSTOMIZED_ANNOTATION_FOLDER, use LINEAPY_HOME_DIR/CUSTOM_ANNOTATIONS_FOLDER_NAME if empty
        elif name == "customized_annotation_folder":
            if self.customized_annotation_folder is None:
                self.set(
                    "customized_annotation_folder",
                    safe_get_folder("home_dir").joinpath(
                        CUSTOM_ANNOTATIONS_FOLDER_NAME
                    ),
                    verbose=False,
                )
            return safe_get_folder("customized_annotation_folder")

        else:
            return self.get(name)


options = lineapy_config()
