from abc import ABC, abstractmethod
from typing import List, Any

from lineapy.data import DirectedEdge, Node
from lineapy.data.types import SessionContext
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.db.base import LineaDBReader, LineaDBWriter


class RelationalLineaDB(LineaDBReader, LineaDBWriter, ABC):
    @abstractmethod
    @property
    def connection(self) -> Any:
        # TODO: define a better output type
        ...

    @property
    def data_asset_manager(self) -> DataAssetManager:
        # TODO
        pass

    def write_nodes(self, nodes: List[Node]) -> None:
        pass

    def write_edges(self, edges: List[DirectedEdge]) -> None:
        pass

    def write_context(self, context: SessionContext):
        pass
