import logging
from pathlib import Path

FOLDER_NAME = ".linea"

LOG_FILE_NAME = "linea.log"


logger = logging.getLogger(__name__)


def linea_folder() -> Path:
    """
    Linea folder exists at the root user level (via `Path.home()`).
    """

    linea_folder = Path.home() / FOLDER_NAME
    if not linea_folder.exists():
        logger.warning(
            "No .linea folder found. Creating a new folder in current directory."
        )
        linea_folder.mkdir(parents=False, exist_ok=True)
    return linea_folder
