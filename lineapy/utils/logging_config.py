"""
Setup logging config for CLI and debugging.

We don't do this in our init, because if imported as a library we don't
want to mess up others logging configuration.
"""

import logging

from rich.console import Console
from rich.logging import RichHandler

from lineapy.utils.config import options

# https://rich.readthedocs.io/en/stable/logging.html#logging-handler

FORMAT = "%(message)s"


def configure_logging(level=None, LOG_SQL=False):
    """
    Configure logging for Lineapy.

    Logging level is read first from the function parameter,
    then lineapy_config options and defaults to INFO.

    This function should be idempotent.
    """

    # Get the loglevel from options or set to INFO if not defined
    level = level or getattr(logging, options.logging_level, logging.INFO)
    # Disable black logging
    # https://github.com/psf/black/issues/2058
    logging.getLogger("blib2to3").setLevel(logging.ERROR)

    # Set SQL log levels to match alembic.ini file if LOG_SQL is set,
    # otherwise suppress warnings
    if LOG_SQL:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARN)
        logging.getLogger("alembic").setLevel(logging.WARN)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
        logging.getLogger("alembic").setLevel(logging.ERROR)

    # Configure root Logger
    logger = logging.getLogger()

    formatter = logging.Formatter(fmt=FORMAT, datefmt="[%X]")
    handler = RichHandler(
        console=Console(stderr=True),
        show_time=False,
        show_path=False,
        show_level=False,
    )
    handler.setFormatter(formatter)

    # Remove old root handler(s).
    # This is to have idempotent behavior for the root logger handlers
    # when configure logging is called multiple times.
    logger.handlers = []
    logger.addHandler(handler)

    logger.setLevel(level=level)
