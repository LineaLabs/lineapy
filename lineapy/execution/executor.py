from abc import abstractmethod

from lineapy.data.graph import Graph
from lineapy.data.types import SessionContext
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.graph_reader.base import GraphReader


class Executor(GraphReader):

    @property
    @abstractmethod
    def data_asset_manager(self) -> DataAssetManager:
        pass

    @abstractmethod
    def setup(self, context: SessionContext) -> None:
        """
        TODO set up the execution environment based on `context`
        """
        pass

    @abstractmethod
    def walk(self, program: Graph) -> None:
        pass
