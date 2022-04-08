import os
import pickle
from pathlib import Path
from typing import Optional

from lineapy.utils.config import FOLDER_NAME, linea_folder

# The name of the database URL environmental variable
DB_URL_ENV_VARIABLE = "LINEA_DATABASE_URL"

# The name for the linea home variable to be formated in the db url
LINEA_HOME_NAME = "LINEA_HOME"

FILE_PICKLER_BASEDIR = "linea_pickles"

DB_FILE_NAME = "db.sqlite"
# Relative path to `db.sqlite` file
# Similar to https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#sql-alchemy-conn
DEFAULT_DB_URL = f"sqlite:///{{{LINEA_HOME_NAME}}}/{DB_FILE_NAME}"

MEMORY_DB_URL = "sqlite:///:memory:"


# Used in functions docstrings which take an optional str as a db url.
OVERRIDE_HELP_TEXT = (
    f"Set the DB URL. If None, will default to reading from the {DB_URL_ENV_VARIABLE}"
    f" env variable and if that is not set then will default to {DEFAULT_DB_URL}."
    f" Note that {{{LINEA_HOME_NAME}}} will be replaced with the root linea home directory."
    f" This is the first directory found which has a {FOLDER_NAME} folder"
)


def resolve_db_url(override_url_template: Optional[str]) -> str:
    template_str = (
        override_url_template
        if override_url_template
        else (
            os.environ.get(DB_URL_ENV_VARIABLE, DEFAULT_DB_URL)
            or DEFAULT_DB_URL  # doing this to avoid the case where the env var is set to blank string
        )
    )
    return template_str.format(**{LINEA_HOME_NAME: linea_folder()})


def resolve_default_db_path() -> Path:
    return linea_folder() / DB_FILE_NAME


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
