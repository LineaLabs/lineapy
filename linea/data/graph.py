from typing import List

from linea.data.types import Node, DirectedEdge


class Graph(object):

    def __init__(self, nodes: List[Node], edges: List[DirectedEdge]):
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
