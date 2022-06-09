import logging
import os
import pickle
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from lineapy.utils.constants import (
    ARTIFACT_MIN_VERSION,
    DB_SQLITE_PREFIX,
    SQLALCHEMY_ECHO,
)

logger = logging.getLogger(__name__)


def parse_artifact_version(version) -> Union[int, str]:
    """
    Attempts to parse user-passed artifact version into a valid artifact version.
    A valid artifact version is either
    - postive int
    - string "all" or "latest"

    Raises ValueError on failure to parse known types.
    Raises NotImplementedError on unknown types.
    """

    # if version is a string, it must be 'all', 'latest', or castable to int
    if isinstance(version, str):
        if version in ["all", "latest"]:
            return version
        else:
            try:
                # attempt int cast
                float_casted = float(version)
                version = int(float_casted)
            except ValueError:
                raise ValueError(
                    f"Invalid version {version}\n"
                    + "If version is str, it must be 'latest', 'all', or be castable to an int"
                )

    # handle float case
    if isinstance(version, float):
        version = int(version)

    # if version is int, it must be greater than or equal to min version
    if isinstance(version, int):
        if version >= ARTIFACT_MIN_VERSION:
            return version
        else:
            raise ValueError(
                f"Invalid version {version}\n"
                + f"Version must be greater than or equal to {ARTIFACT_MIN_VERSION}"
            )

    raise NotImplementedError(
        f"Invalid version {version}\n" + "Unable to parse version."
    )


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
