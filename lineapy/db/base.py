from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from lineapy.constants import *
from lineapy.data.graph import Graph
from lineapy.data.types import DataSourceNode, Node
from lineapy.data.types import LineaID, SessionContext
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.utils import CaseNotHandledError


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
    raise CaseNotHandledError("Unknown Execution mode")


class LineaDBReader(ABC):
    """
    TODO: programmatic APIs for querying LineaDB
    """

    def get_node_by_id(self, linea_id: LineaID) -> Node:  # type: ignore
        pass

    def get_graph_from_artifact_id(self, linea_id: LineaID):
        pass

    def find_all_artifacts_derived_from_data_source(
        self, program: Graph, data_source_node: DataSourceNode
    ) -> List[Node]:  # type: ignore
        pass

    def gather_artifact_intermediate_nodes(self, program: Graph):
        """
        While this is on a single graph, it actually requires talking to the data asset manager, so didn't get put into the MetadataExtractor.
        """
        pass


class LineaDBWriter(ABC):
    @property
    @abstractmethod
    def data_asset_manager(self) -> DataAssetManager:
        ...

    @abstractmethod
    def write_nodes(self, nodes: List[Node]) -> None:
        """
        Note that inside write_nodes, you
        """
        ...

    @abstractmethod
    def write_context(self, context: SessionContext):
        ...


class LineaDB(LineaDBReader, LineaDBWriter, ABC):
    @abstractmethod
    def init_db(self, db_config: LineaDBConfig):
        ...
