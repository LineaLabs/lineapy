from lineapy.constants import ExecutionMode
from lineapy.db.base import DatabaseOption, FileSystemOption
from lineapy.db.base import LineaDBConfig


def get_linea_db_config_from_execution_mode(
    execution_mode: ExecutionMode,
) -> LineaDBConfig:
    if execution_mode == ExecutionMode.TEST:
        return LineaDBConfig(
            database=DatabaseOption.SQLite,
            file_system=FileSystemOption.Local,
            database_uri="sqlite:///e2e_test.sqlite",
        )
    if execution_mode == ExecutionMode.DEV:
        return LineaDBConfig(
            database=DatabaseOption.SQLite,
            file_system=FileSystemOption.Local,
            database_uri="sqlite:///dev.sqlite",
        )
    else:
        raise NotImplementedError("Production mode is not yet supported")
