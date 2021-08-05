from abc import ABC, abstractmethod

from lineapy.data.graph import Graph
from lineapy.data.types import SessionContext
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.graph_reader.base import GraphReader


class Executor(GraphReader):
    @property
    @abstractmethod
    def context(self) -> SessionContext:
        """ """
        pass

    @property
    @abstractmethod
    def data_asset_manager(self) -> DataAssetManager:
        pass

    @abstractmethod
    def setup(self) -> None:
        """
        TODO
        - install libraries based on `SessionContext`
        Examples of setup tasks:
            -
            - start Airflow executor
            - set up Spark cluster.
        """
        pass

    @abstractmethod
    def walk(self, program: Graph) -> None:
        # TODO: new type for `program`?
        pass


# TODO: implement Executor based on Airflow
