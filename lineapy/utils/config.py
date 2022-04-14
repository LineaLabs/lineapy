import logging
from pathlib import Path

FOLDER_NAME = ".linea"

LOG_FILE_NAME = "linea.log"


logger = logging.getLogger(__name__)


def linea_folder() -> Path:
    """
    Linea folder exists at the root user level (via `Path.home()`).
    """
    # TODO: add a special case for tests (or some scoping config)
    linea_folder = Path.home() / FOLDER_NAME
    if not linea_folder.exists():
        logger.warning(
            f"No {FOLDER_NAME} folder found. Creating a new folder in {Path.home()} directory."
        )
        linea_folder.mkdir(parents=False, exist_ok=True)
    return linea_folder
