from typing import List, Dict, Optional, Any, cast

import networkx as nx

from lineapy.data.types import *


class Graph(object):
    def __init__(self, nodes: List[Node]):
        """
        Note:
        - edges could be none for very simple programs
        """
        self._nodes: List[Node] = nodes
        self._ids: Dict[LineaID, Node] = dict((n.id, n) for n in nodes)
        self._edges: List[DirectedEdge] = Graph.__get_edges_from_nodes(nodes)
        self._nx_graph = nx.DiGraph()
        self._nx_graph.add_nodes_from([node.id for node in nodes])
        self._nx_graph.add_edges_from(
            [(edge.source_node_id, edge.sink_node_id) for edge in self._edges]
        )

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
        return list(self.nx_graph.predecessors(node))

    def get_ancestors(self, node: Node) -> List[LineaID]:
        return list(nx.ancestors(self.nx_graph, node))

    def get_children(self, node: Node) -> List[LineaID]:
        return list(self.nx_graph.successors(node))

    def get_descendants(self, node: Node) -> List[LineaID]:
        return list(nx.descendants(self.nx_graph, node))

    def get_node(self, node_id: Optional[LineaID]) -> Optional[Node]:
        if node_id in self.ids:
            return self.ids[node_id]
        return None

    def get_node_value(self, node: Optional[Node]) -> Optional[NodeValue]:
        if node is None:
            return None

        # find the original source node in a chain of aliases
        if node.node_type is NodeType.VariableAliasNode:
            node = cast(VariableAliasNode, node)
            source = self.get_node(node.source_variable_id)
            if source is None:
                print("WARNING: Could not find source node from id.")
                return None

            if source.node_type is NodeType.VariableAliasNode:
                source = cast(VariableAliasNode, source)

                while (
                    source is not None
                    and source.node_type is NodeType.VariableAliasNode
                ):
                    source = cast(VariableAliasNode, source)
                    source = self.get_node(source.source_variable_id)

            return source.value

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

        else:
            return node.value

    def get_node_value_from_id(self, node_id: Optional[LineaID]) -> Optional[Any]:
        node = self.get_node(node_id)
        return self.get_node_value(node)

    def get_arguments_from_call_node(self, node: CallNode) -> List[NodeValue]:
        args = [self.get_node(a) for a in node.arguments]

        # NOTE: for cases where a large list is being instantiated using the list constructor, this may add unwanted overhead
        # can use operator.attrgetter instead of x.positional_order to speed up this process
        args.sort(key=lambda x: x.positional_order)
        return [self.get_node_value(a) for a in args]

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
            if node.state_change_nodes is not None:
                source_nodes.extend(node.state_change_nodes)
            if node.import_nodes is not None:
                source_nodes.extend(node.import_nodes)
            if (
                node.node_type is NodeType.ConditionNode
                and node.dependent_variables_in_predicate is not None
            ):
                source_nodes.extend(node.dependent_variables_in_predicate)
        elif node.node_type is StateChangeNode:
            node = cast(StateChangeNode, node)
            source_nodes.append(node.associated_node_id)
            source_nodes.append(node.initial_value_node_id)
        elif node.node_type is NodeType.LiteralAssignNode:
            node = cast(LiteralAssignNode, node)
            if node.value_node_id is not None:
                source_nodes.append(node.value_node_id)
        elif node.node_type is NodeType.VariableAliasNode:
            node = cast(VariableAliasNode, node)
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

        edges = list(map(add_edge_from_node, Graph.get_parents_from_node(node)))
        return edges

    def print(self):
        for n in self._nodes:
            print(n)
        for e in self._edges:
            print(e)

    def __str__(self):
        self.print()

    def __repr__(self):
        self.print()
