from abc import ABC, abstractmethod
from typing import List

from linea.dataflow.data_types import Node, DirectedEdge, SessionContext
from linea.db.asset_manager.base import DataAssetManager


class LineaDBReader(ABC):
    """
    TODO: programmatic APIs for querying LineaDB
    """
    pass


class LineaDBWriter(ABC):

    @abstractmethod
    @property
    def data_asset_manager(self) -> DataAssetManager:
        ...

    @abstractmethod
    def write_nodes(self, nodes: List[Node]) -> None:
        ...

    @abstractmethod
    def write_edges(self, edges: List[DirectedEdge]) -> None:
        ...

    @abstractmethod
    def write_context(self, context: SessionContext):
        ...


