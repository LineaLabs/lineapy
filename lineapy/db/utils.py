import logging
import os
import pickle
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from lineapy.utils.constants import DB_SQLITE_PREFIX, SQLALCHEMY_ECHO

logger = logging.getLogger(__name__)


def is_artifact_version_valid(version: Union[int, str]):
    if isinstance(version, int) and version >= 0:
        return True
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
