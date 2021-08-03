from abc import ABC, abstractmethod

from linea.data.graph import Graph


class GraphReader(ABC):
    """
    Base class for anything that only involves reading the graph
    without writing anything back to the DB.

    TODO
    """

    @abstractmethod
    def walk(self, graph: Graph):
        pass
