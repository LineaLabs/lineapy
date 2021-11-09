from pathlib import Path

FOLDER_NAME = ".linea"


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
    raise RuntimeError("No .linea directory found.")
