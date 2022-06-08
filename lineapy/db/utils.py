import logging
import os
import pickle
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from lineapy.utils.constants import DB_SQLITE_PREFIX, SQLALCHEMY_ECHO

logger = logging.getLogger(__name__)


def parse_artifact_version(version: object) -> Union[int, str]:
    """
    Attempts to parse user-passed artifact version into a valid artifact version.
    A valid artifact version is either
    - postive int
    - string "all" or "latest"

    Raises ValueError on failure.
    """
    # attempt int cast
    try:
        casted_version = int(version)
        if casted_version >= 0:
            return casted_version
        else:
            raise ValueError(f"Invalid version {version}\n" + "Version must either be a number >= 0  or a string \'all\' or \'nothing\'")
    except ValueError:
        pass

    # attempt float cast
    try:
        casted_version = float(version)
        if casted_version >= 0:
            return int(casted_version)
        else:
            raise ValueError(f"Invalid version {version}\n" + "Version must either be a number >= 0  or a string \'all\' or \'nothing\'")
    except ValueError:
        pass

    # attempt to cast to either 'all' or 'latest'
    try:
        casted_version = str(version)
        if casted_version in ["all", "latest"]:
            return casted_version
        else:
            raise ValueError(f"Invalid version {version}\n" + "Version must either be a number >= 0  or a string \'all\' or \'nothing\'")
    except ValueError:
        raise ValueError(f"Invalid version {version}\n" + "Version must either be a number >= 0  or a string \'all\' or \'nothing\'")


def is_artifact_version_valid(version: Union[int, str]):
    if isinstance(version, int) and version >= 0:
        return True
    if not isinstance(version, str):
        return False
    if version in ["all", "latest"]:
        return True
    try:
        casted_version = int(version)
        return casted_version >= 0
    except ValueError:
        return False


def create_lineadb_engine(url: str) -> Engine:
    """Create a SQLAlchemy engine for LineaDB.
    Take care of the SQLite database file name and configuration.
    """
    echo = os.getenv(SQLALCHEMY_ECHO, default="false").lower() == "true"
    logger.debug(f"Connecting to Linea DB at {url}")
    additional_args = {}
    if url.startswith(DB_SQLITE_PREFIX):
        additional_args = {"check_same_thread": False}
    return create_engine(
        url,
        connect_args=additional_args,
        poolclass=StaticPool,
        echo=echo,
    )


class FilePickler:
    """
    Tries to pickle an object, and if it fails returns None.
    """

    @staticmethod
    def dump(value, fileobj, protocol=pickle.HIGHEST_PROTOCOL):
        if fileobj is None:
            return None
        try:
            return pickle.dump(value, fileobj, protocol)
        except pickle.PicklingError:
            return None

    @staticmethod
    def load(fileobj):
        return pickle.load(fileobj)
