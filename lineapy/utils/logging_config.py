"""
Setup logging config for CLI and debugging.

We don't do this in our init, because if imported as a library we don't
want to mess up others logging configuration.
"""

import logging
import os

from rich.console import Console
from rich.logging import RichHandler

# https://rich.readthedocs.io/en/stable/logging.html#logging-handler

FORMAT = "%(message)s"


LOGGING_ENV_VARIABLE = "LINEA_LOG_LEVEL"


def configure_logging(level=None, LOG_SQL=False):
    # Get the loglevel from `LOGGING_ENV_VARIABLE` or set to WARNING
    # if not defined
    level = level or os.environ.get(LOGGING_ENV_VARIABLE, logging.INFO)
    # Disable black logging
    # https://github.com/psf/black/issues/2058
    logging.getLogger("blib2to3").setLevel(logging.ERROR)

    if LOG_SQL:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    logging.basicConfig(
        level=level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                show_time=False,
                show_path=False,
                show_level=False,
            )
        ],
    )
