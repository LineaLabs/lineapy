import collections
import enum
import re
from typing import cast, List, Dict, Optional, Any
from dataclasses import dataclass, field
import typing
import black
import networkx as nx
from pydantic import BaseModel
from pydantic.fields import SHAPE_LIST, SHAPE_SINGLETON

from lineapy.data.types import (
    LineaID,
    Node,
    ArgumentNode,
    NodeValueType,
    NodeType,
    CallNode,
    SideEffectsNode,
    StateChangeNode,
    VariableNode,
    StateDependencyType,
    DataSourceNode,
    ImportNode,
)
from lineapy.graph_reader.graph_helper import get_arg_position
from lineapy.utils import InternalLogicError, NullValueError


@dataclass
class DirectedEdge:
    """
    `DirectedEdge` is only used by the Graph to constructure dependencies
      so that we can use `networkx` directly.
    """

    source_node_id: LineaID
    sink_node_id: LineaID


class Graph(object):
    def __init__(self, nodes: List[Node]):
        """
        Note:
        - edges could be none for very simple programs
        """
        self._nodes: List[Node] = nodes
        self._ids: Dict[LineaID, Node] = dict((n.id, n) for n in nodes)
        self._nx_graph = nx.DiGraph()
        self._nx_graph.add_nodes_from([node.id for node in nodes])

        self._edges: List[DirectedEdge] = Graph.__get_edges_from_nodes(nodes)
        self._nx_graph.add_edges_from(
            [(edge.source_node_id, edge.sink_node_id) for edge in self._edges]
        )
        self._nx_graph.add_edges_from(
            [
                (edge.source_node_id, edge.sink_node_id)
                for edge in self.__get_edges_from_line_number()
            ]
        )

        self.print = GraphPrinter(self)
        if not nx.is_directed_acyclic_graph(self._nx_graph):
            raise InternalLogicError("Graph should not be cyclic")

    @property
    def nx_graph(self) -> nx.DiGraph:
        return self._nx_graph

    @property
    def ids(self) -> Dict[LineaID, Node]:
        return self._ids

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    def visit_order(self) -> List[LineaID]:
        return list(nx.topological_sort(self.nx_graph))

    def get_parents(self, node: Node) -> List[LineaID]:
        return list(self.nx_graph.predecessors(node.id))

    def get_ancestors(self, node: Node) -> List[LineaID]:
        return list(nx.ancestors(self.nx_graph, node.id))

    def get_children(self, node: Node) -> List[LineaID]:
        return list(self.nx_graph.successors(node.id))

    def get_descendants(self, node: Node) -> List[LineaID]:
        return list(nx.descendants(self.nx_graph, node.id))

    def get_node(self, node_id: Optional[LineaID]) -> Optional[Node]:
        if node_id is not None and node_id in self.ids:
            return self.ids[node_id]
        return None

    def get_node_else_raise(self, node_id: LineaID) -> Node:
        if node_id is None or node_id not in self.ids:
            raise NullValueError(f"Could not find {node_id}")
        return self.ids[node_id]

    def get_node_value(self, node: Optional[Node]) -> Optional[NodeValueType]:
        if node is None:
            return None

        # find the original source node in a chain of aliases
        if node.node_type is NodeType.VariableNode:
            node = cast(VariableNode, node)
            source = self.get_node(node.source_variable_id)
            if source is None:
                print("WARNING: Could not find source node from id.")
                return None

            if source.node_type is NodeType.VariableNode:
                source = cast(VariableNode, source)

                while (
                    source is not None
                    and source.node_type is NodeType.VariableNode
                ):
                    source = cast(VariableNode, source)
                    source = self.get_node(source.source_variable_id)

            return source.value  # type: ignore

        elif node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNode, node)
            if node.value_literal is not None:
                return node.value_literal
            elif node.value_node_id is not None:
                return self.get_node_value(self.get_node(node.value_node_id))
            return None

        elif node.node_type is NodeType.DataSourceNode:
            node = cast(DataSourceNode, node)
            return node.access_path

        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNode, node)
            return node.module
        else:
            return node.value  # type: ignore

    def get_node_value_from_id(
        self, node_id: Optional[LineaID]
    ) -> Optional[Any]:
        node = self.get_node(node_id)
        return self.get_node_value(node)

    def get_arguments_from_call_node(
        self, node: CallNode
    ) -> tuple[List[NodeValueType], dict[str, NodeValueType]]:
        """
        FIXME: rather than using our loop comprehension, we should rely
          on database joins
        """
        arg_nodes = []
        kwarg_values = {}
        # Iterate through arguments and append to args/kwargs
        for arg in node.arguments:
            argument_node = cast(ArgumentNode, self.get_node_else_raise(arg))
            if argument_node.keyword is not None:
                kwarg_values[argument_node.keyword] = self.get_node_value(
                    argument_node
                )
            else:
                arg_nodes.append(argument_node)

        arg_nodes.sort(key=get_arg_position)

        return [self.get_node_value(a) for a in arg_nodes], kwarg_values

    # getting a node's parents before the graph has been constructed
    @staticmethod
    def get_parents_from_node(node: Node) -> List[LineaID]:
        source_nodes = []

        if node.node_type is NodeType.CallNode:
            node = cast(CallNode, node)
            source_nodes.extend(node.arguments)
            if node.function_module is not None:
                source_nodes.append(node.function_module)
            if node.locally_defined_function_id is not None:
                source_nodes.append(node.locally_defined_function_id)
        elif node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNode, node)
            if node.value_node_id is not None:
                source_nodes.append(node.value_node_id)
        elif node.node_type in [
            NodeType.LoopNode,
            NodeType.ConditionNode,
            NodeType.FunctionDefinitionNode,
        ]:
            node = cast(SideEffectsNode, node)
            if node.import_nodes is not None:
                source_nodes.extend(node.import_nodes)
            if node.input_state_change_nodes is not None:
                source_nodes.extend(node.input_state_change_nodes)
        elif node.node_type is NodeType.StateChangeNode:
            node = cast(StateChangeNode, node)
            if node.state_dependency_type is StateDependencyType.Write:
                source_nodes.append(node.associated_node_id)
            elif node.state_dependency_type is StateDependencyType.Read:
                source_nodes.append(node.initial_value_node_id)
        elif node.node_type is NodeType.VariableNode:
            node = cast(VariableNode, node)
            source_nodes.append(node.source_variable_id)

        return source_nodes

    @staticmethod
    def __get_edges_from_nodes(nodes: List[Node]) -> List[DirectedEdge]:
        edges = []
        for node in nodes:
            edges.extend(Graph.__get_edges_to_node(node))
        return edges

    @staticmethod
    def __get_edges_to_node(node: Node) -> List[DirectedEdge]:
        def add_edge_from_node(id: LineaID) -> DirectedEdge:
            return DirectedEdge(source_node_id=id, sink_node_id=node.id)

        edges = list(
            map(add_edge_from_node, Graph.get_parents_from_node(node))
        )
        return edges

    def __get_edges_from_line_number(self) -> List[DirectedEdge]:
        edges = []
        # find all data source nodes
        for node in self.nodes:
            if node.node_type is NodeType.DataSourceNode:
                descendants = [
                    n
                    for n in self.get_descendants(node)
                    if n is not None
                    and self.get_node_else_raise(n).node_type
                    is NodeType.CallNode
                ]

                # sort data source nodes children
                descendants.sort(
                    key=lambda n: self.get_node_else_raise(n).lineno
                )
                # add edges between children
                for d in range(len(descendants) - 1):
                    if self.nx_graph.has_edge(
                        descendants[d], descendants[d + 1]
                    ) or self.nx_graph.has_edge(
                        descendants[d + 1], descendants[d]
                    ):
                        continue
                    edges.append(
                        DirectedEdge(
                            source_node_id=descendants[d],
                            sink_node_id=descendants[d + 1],
                        )
                    )
        # print(edges)
        return edges

    def __str__(self):
        return self.print()

    def __repr__(self):
        return self.print()


@dataclass
class GraphPrinter:
    """
    Pretty prints a graph, in a similar way as how you would create it by hand.

    This represenation should be consistant despite UUIDs being different.
    """

    graph: Graph
    id_to_attribute_name: dict[LineaID, str] = field(default_factory=dict)

    # Mapping of each node types to the count of nodes of that type printed so far,
    # to create variables based on node type.
    node_type_to_count: dict[NodeType, int] = field(
        default_factory=lambda: collections.defaultdict(lambda: 0)
    )

    def __call__(self) -> Any:
        s = "\n".join(self.lines())
        return black.format_str(s, mode=black.Mode())

    def get_node_type_count(self, node_type: NodeType) -> int:
        prev = self.node_type_to_count[node_type]
        next = prev + 1
        self.node_type_to_count[node_type] = next
        return next

    def get_node_type_name(self, node_type: NodeType) -> str:
        return f"{pretty_print_node_type(node_type)}_{self.get_node_type_count(node_type)}"

    def lines(self) -> typing.Iterable[str]:
        yield "from lineapy.data.types import *"
        yield "from lineapy.utils import get_new_id"
        yield "session_id = get_new_id()"
        for node_id in self.graph.visit_order():
            node = self.graph.ids[node_id]
            attr_name = self.get_node_type_name(node.node_type)
            self.id_to_attribute_name[node_id] = attr_name
            yield f"{attr_name} = ("
            yield from self.pretty_print_model(node)
            yield ")"

    def pretty_print_model(self, model: BaseModel) -> typing.Iterable[str]:
        yield f"{type(model).__name__}("
        yield from self.pretty_print_node_lines(model)
        yield ")"

    def lookup_id(self, id: LineaID) -> str:
        return self.id_to_attribute_name[id] + ".id"

    def pretty_print_node_lines(self, node: BaseModel) -> typing.Iterable[str]:
        for k in node.__fields__.keys():
            v = getattr(node, k)
            field = node.__fields__[k]
            tp = field.type_
            shape = field.shape
            v_str: str
            if k == "node_type":
                continue
            elif k == "id":
                v_str = "get_new_id()"
            elif k == "session_id":
                v_str = "session_id"
            elif tp == LineaID and shape == SHAPE_LIST and v is not None:
                args = [self.lookup_id(id_) for id_ in v]
                # Arguments are unordered, even though they are lists not sets,
                # so sort them before exporting
                if k == "arguments":
                    args.sort()
                v_str = "[" + ", ".join(args) + "]"
            # Singleton NewTypes get cast to str by pydantic, so we can't differentiate at the field
            # level between them and strings, so we just see if can look up the ID
            elif isinstance(v, str) and v in self.id_to_attribute_name:  # type: ignore
                v_str = self.lookup_id(v)  # type: ignore
            else:
                v_str = "\n".join(self.pretty_print_value(v))
            yield f"{k}={v_str},"

    def pretty_print_value(self, v: object) -> typing.Iterable[str]:
        if isinstance(v, enum.Enum):
            yield v.name
        elif isinstance(v, BaseModel):
            yield from self.pretty_print_model(v)
        else:
            yield repr(v)


def pretty_print_node_type(type: NodeType) -> str:
    """
    Turns a node type into something that can be used as a variable name.
    """
    return camel_to_snake_case(type.name.replace("Node", ""))


# https://stackoverflow.com/a/1176023/907060
camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake_case(s: str) -> str:
    return camel_case_pattern.sub("_", s).lower()
