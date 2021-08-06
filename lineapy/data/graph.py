from typing import List

from lineapy.data.types import Node, DirectedEdge


class Graph(object):
    """
    TODO:
    - implement the getters by wrapping around networkx (see https://github.com/LineaLabs/backend-take-home/blob/main/dag.py for simple reference)
    """

    def __init__(self, nodes: List[Node], edges: List[DirectedEdge] = []):
        """
        Note:
        - edges could be none for very simple programs
        """
        self._nodes: List[Node] = nodes
        self._edges: List[DirectedEdge] = edges

    def get_parents(self, node: Node) -> List[Node]:
        # TODO
        ...

    def get_ancestors(self, node: Node) -> List[Node]:
        # TODO
        ...

    def get_children(self, node: Node) -> List[Node]:
        # TODO
        ...

    def get_descendants(self, node: Node) -> List[Node]:
        # TODO
        ...

    def print(self):
        # TODO: improve printing (cc @dhruv)
        for n in self._nodes:
            print(n)
        for e in self._edges:
            print(e)

    def __str__(self):
        self.print()

    def __repr__(self):
        self.print()
