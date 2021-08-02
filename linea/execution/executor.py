from abc import ABC, abstractmethod

from linea.data.types import SessionContext
from linea.db.asset_manager.base import DataAssetManager
from linea.db.base import LineaDB
from linea.graph_reader.base import GraphReader


class Executor(ABC, GraphReader):

    @property
    @abstractmethod
    def context(self) -> SessionContext:
        pass

    @property
    @abstractmethod
    def lineadb(self) -> LineaDB:
        pass

    @property
    @abstractmethod
    def data_asset_manager(self) -> DataAssetManager:
        pass

    @abstractmethod
    def setup(self) -> None:
        """
        TODO set up the environment based on some config (e.g., `SessionContext`)
        Examples of setup tasks:
            - install libraries
            - start Airflow executor
            - set up Spark cluster.
        """
        pass

    @abstractmethod
    def run(self, program: str) -> None:
        # TODO: new type for `program`?
        pass

# TODO: implement Executor based on Airflow
