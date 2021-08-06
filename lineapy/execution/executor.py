from abc import ABC, abstractmethod
from typing import Any

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
        Sets up the execution environment
        TODO
        - install libraries based on `SessionContext`
        Examples of future setup tasks (out of scope for the current iteration)
            - start Airflow executor
            - set up Spark cluster.
        """
        pass

    def get_stdout(self) -> str:
        """
        This returns the text that corresponds to the stdout results.
        For instance, `print("hi")` should yield a result of "hi\n" from this function.

        Note:
        - If we assume that everything is sliced, the user printing may not happen, but third party libs may still have outputs.
        - Also the user may manually annotate for the print line to be included and in general stdouts are useful
        """
        pass

    def get_value_by_varable_name(self, name: str) -> Any:
        pass

    @abstractmethod
    def walk(self, program: Graph) -> None:
        pass
