import logging
from pathlib import Path

FOLDER_NAME = ".lineapy"

LOG_FILE_NAME = "linea.log"

CUSTOM_ANNOTATIONS_FOLDER_NAME = "custom-annotations"

CUSTOM_ANNOTATIONS_EXTENSION_NAME = ".annotations.yaml"

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


def custom_annotations_folder() -> Path:
    """
    Where annotations are stored within linea folder.
    """
    parent = linea_folder()
    annotate_folder = parent / CUSTOM_ANNOTATIONS_FOLDER_NAME
    if not annotate_folder.exists():
        logger.warning(
            f"No {CUSTOM_ANNOTATIONS_FOLDER_NAME} folder found. Creating a new folder in {parent} directory."
        )
        annotate_folder.mkdir(parents=False, exist_ok=True)
    return annotate_folder
