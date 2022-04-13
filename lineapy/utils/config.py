import logging
from pathlib import Path

FOLDER_NAME = ".linea"

LOG_FILE_NAME = "linea.log"


logger = logging.getLogger(__name__)


def linea_folder() -> Path:
    """
    Finds the closest `.linea` folder, raising an exception if one does not exist.
    """
    cwd = Path(".").resolve()
    for i, dir in enumerate([cwd, *cwd.parents]):
        possible_linea_folder = dir / FOLDER_NAME
        if possible_linea_folder.is_dir():
            # Return path relative to CWD, so that it is stable
            # regardles of parent path in subdirectories
            # for notebook output
            return Path("./" + "../" * i) / FOLDER_NAME

    # you are here because you could not find a .linea folder anywhere. #418 says create one.
    logger.warning(
        "No .linea folder found. Creating a new folder in current directory."
    )
    cwd_linea_folder = Path(".").resolve() / FOLDER_NAME
    cwd_linea_folder.mkdir(parents=False, exist_ok=True)
    return cwd_linea_folder
