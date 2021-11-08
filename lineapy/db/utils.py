import os

DB_URL_ENV_VARIABLE = "LINEA_DB_URL"
# Relative path to `linea.sqlite` file
# TODO: Possibly move to `.linea` directory, and use this in URL like airflow
# does https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#sql-alchemy-conn
# sqlite:///{AIRFLOW_HOME}/airflow.db
DEFAULT_DB_URL = "sqlite:///linea.sqlite"

MEMORY_DB_URL = "sqlite:///:memory:"


# Used in functions docstrings which take an optional str as a db url.
OVERRIDE_HELP_TEXT = (
    f"Set the DB URL. If None, will default to reading from the {DB_URL_ENV_VARIABLE}"
    f" env variable and if that is not set then will default to {DEFAULT_DB_URL}"
)


def lookup_db_url() -> str:
    """
    Looks up the DB URL from the environment or uses the default
    """
    return os.environ.get(DB_URL_ENV_VARIABLE, DEFAULT_DB_URL)
