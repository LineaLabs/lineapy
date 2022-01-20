"""
Setup logging config for CLI and debugging.

We don't do this in our init, because if imported as a library we don't
want to mess up others logging configuration.
"""

import logging

from rich.logging import RichHandler

# https://rich.readthedocs.io/en/stable/logging.html#logging-handler

FORMAT = "%(message)s"


def configure_logging(level="WARNING", LOG_SQL=False):
    # Disable black logging
    # https://github.com/psf/black/issues/2058
    logging.getLogger("blib2to3").setLevel(logging.ERROR)

    if LOG_SQL:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    logging.basicConfig(
        level=level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
