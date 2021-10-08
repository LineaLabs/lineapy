from dataclasses import dataclass
from enum import Enum

from lineapy.constants import (
    DEV_DATABASE_URI,
    MEMORY_DATABASE_URI,
    PROD_DATABASE_URI,
    TEST_DATABASE_URI,
    ExecutionMode,
)


class DatabaseOption(Enum):
    SQLite = 1


class FileSystemOption(Enum):
    Local = 1
    S3 = 2  # Net yet implemented


@dataclass
class LineaDBConfig:

    database_uri: str
    database: DatabaseOption = DatabaseOption.SQLite
    file_system: FileSystemOption = FileSystemOption.Local


def get_default_config_by_environment(mode: ExecutionMode) -> LineaDBConfig:
    if mode == ExecutionMode.DEV:
        return LineaDBConfig(database_uri=DEV_DATABASE_URI)
    if mode == ExecutionMode.TEST:
        return LineaDBConfig(database_uri=TEST_DATABASE_URI)
    if mode == ExecutionMode.PROD:
        return LineaDBConfig(database_uri=PROD_DATABASE_URI)
    if mode == ExecutionMode.MEMORY:
        return LineaDBConfig(database_uri=MEMORY_DATABASE_URI)
    raise ValueError("Unknown Execution mode")
