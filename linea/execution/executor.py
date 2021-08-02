from abc import ABC, abstractmethod

from linea.data.types import SessionContext
from linea.db.asset_manager.base import DataAssetManager
from linea.db.base import LineaDB


class Executor(ABC):

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
        pass

    @abstractmethod
    def run(self, program: str) -> None:
        # TODO: new type for `program`?
        pass

# TODO: implement Executor based on Airflow
