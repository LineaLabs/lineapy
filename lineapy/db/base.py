from enum import Enum
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

from lineapy.data.types import LineaID, Node, DirectedEdge, SessionContext
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.data.types import DataSourceNode, Node
from lineapy.data.graph import Graph


class DatabaseOption(Enum):
    SQLite = 1


class FileSystemOption(Enum):
    Local = 1
    S3 = 2  # #dhruv don't worry about S3 for now.


@dataclass
class LineaDbConfig:
    """
    @dorx please review this config, maybe this is NOT what you had in mind
    """

    database: DatabaseOption = DatabaseOption.SQLite
    file_system: FileSystemOption = FileSystemOption.Local


class LineaDBReader(ABC):
    """
    TODO: programmatic APIs for querying LineaDB
    """

    def get_node_by_id(self, linea_id: LineaID) -> Node:
        pass

    def get_graph_from_artifact_id(self, linea_id: LineaID):
        # @dhruv high priority implementation once you have the db writer done
        pass

    def find_all_artifacts_derived_from_data_source(
        self, program: Graph, data_source_node: DataSourceNode
    ) -> List[Node]:
        # @dhruv: high priority implmenetation once you have the asset manager and relational done.
        pass

    def gather_artifact_intermediate_nodes(self, program: Graph):
        """
        While this is on a single graph, it actually requires talking to the data asset manager, so didn't get put into the MetadataExtractor.
        """
        pass


class LineaDBWriter(ABC):
    @abstractmethod
    @property
    def data_asset_manager(self) -> DataAssetManager:
        ...

    @abstractmethod
    def write_nodes(self, nodes: List[Node]) -> None:
        """
        Note that inside write_nodes, you
        """
        ...

    @abstractmethod
    def write_edges(self, edges: List[DirectedEdge]) -> None:
        ...

    @abstractmethod
    def write_context(self, context: SessionContext):
        ...
