"""
An abstract graph representation that is conducive to being visualized easily.

We include in this graph:

* From the DB about this session:
  * Nodes
  * Artifacts
  * Source code
* From the tracer:
  * Mutation and view edges
  * Variables

We currently don't include, but could:

* Node values
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Union

from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    GlobalNode,
    ImportNode,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
    NodeType,
)
from lineapy.instrumentation.tracer import Tracer


@dataclass
class VisualGraphOptions:
    """
    Class to store options for the visualizer, so that we can properly type them
    as we pass this down the stack.
    """

    graph: Graph
    # The tracer is optional, if provided, will let us show some additional
    # information, like variables.
    tracer: Optional[Tracer]

    # Whether to highlight a certain node.
    # For now, this will only show that node and its ancestors.
    # In the future, it will grey out the rest, but still show them
    highlight_node: Optional[str]
    # Whether to add edges for the implied views in the tracer (requires tracer)
    show_implied_mutations: bool
    # Whether to add edges for the views kept in the tracer (requires tracer)
    show_views: bool
    # Whether to show artifacts (requires tracer)
    show_artifacts: bool
    # Whether to show variables (requires tracer)
    show_variables: bool


def to_visual_graph(options: VisualGraphOptions) -> VisualGraph:
    """
    Returns a visual graph based on the options.
    """
    tracer = options.tracer
    graph = options.graph
    vg = VisualGraph()

    # We will create some mappings to start, so that we can add the
    # variables and artifacts to each node

    # First create a mapping of each node ID to all of its artifact names
    id_to_artifacts: Dict[str, List[Optional[str]]] = defaultdict(list)
    if options.show_artifacts:
        if not tracer:
            raise RuntimeError("Cannot show artifacts without tracer")
        for a in tracer.session_artifacts():
            id_to_artifacts[a.node_id].append(a.name)

    # Then create a mapping of each node to the variables which point to it
    id_to_variables: Dict[str, List[str]] = defaultdict(list)
    if options.show_variables:
        if not tracer:
            raise RuntimeError("Cannot show implied mutations without tracer")
        for name, node in tracer.variable_name_to_node.items():
            id_to_variables[node.id].append(name)

    # First add all the nodes from the session
    for node in graph.nodes:
        extra_labels = [
            ExtraLabel(a or "Unnamed Artifact", ExtraLabelType.ARTIFACT)
            for a in id_to_artifacts[node.id]
        ] + [
            ExtraLabel(v, ExtraLabelType.VARIABLE)
            for v in id_to_variables[node.id]
        ]
        contents = process_node(vg, node, options)
        vg.node(VisualNode(node.id, node.node_type, contents, extra_labels))

    # For now, our algorithm for making nodes based on source locations is:
    # 1. Whenever we encounter a node, if we haven't made a source code node
    #    for that pair of start and end lines, make one and add an edge
    #    from the previous to it.
    # 2. We add an edge from that source node to the node.

    # This assumes that we iterate through nodes in line order, and that
    #  we skip printing any lines that don't appear in nodes.
    # It also assumes that we have no overlapping line number ranges,
    # i.e. a node that is from lines 1-3 and another node just on line 3
    # If this does occur, we will end up print line 3's source code twice.

    added_source_ids: Set[str] = set()
    last_added_source_id: Optional[str] = None

    # Then add the source code nodes
    for n in graph.nodes:
        source_location = n.source_location
        if not source_location:
            continue
        id_ = f"{source_location.source_code.id}-{source_location.lineno}-{source_location.end_lineno}"
        if id_ not in added_source_ids:
            added_source_ids.add(id_)
            # Use \l instead of \n for left aligned code
            contents = (
                r"\l".join(
                    source_location.source_code.code.splitlines()[
                        source_location.lineno - 1 : source_location.end_lineno
                    ]
                )
                + r"\l"
            )
            vg.node(VisualNode(id_, SourceLineType(), contents, []))

            if last_added_source_id:
                vg.edge(
                    VisualEdge(
                        VisualEdgeID(last_added_source_id),
                        VisualEdgeID(id_),
                        VisualEdgeType.NEXT_LINE,
                    )
                )
            last_added_source_id = id_
        vg.edge(
            VisualEdge(
                VisualEdgeID(id_),
                VisualEdgeID(n.id),
                VisualEdgeType.SOURCE_CODE,
            )
        )
    # Then we can add all the additional information from the tracer
    if options.show_implied_mutations:
        if not tracer:
            raise RuntimeError("Cannot show implied mutations without tracer")
        # the mutate nodes
        for source, mutate in tracer.mutation_tracker.source_to_mutate.items():
            vg.edge(
                VisualEdge(
                    VisualEdgeID(source),
                    VisualEdgeID(mutate),
                    VisualEdgeType.LATEST_MUTATE_SOURCE,
                )
            )

    if options.show_views:
        if not tracer:
            raise RuntimeError("Cannot show views without tracer")

        # Create a set of unique pairs of viewers, where order doesn't matter
        # Since they aren't directed
        viewer_pairs: Set[FrozenSet[LineaID]] = {
            frozenset([source, viewer])
            for source, viewers in tracer.mutation_tracker.viewers.items()
            for viewer in viewers
        }
        for source, target in viewer_pairs:
            vg.edge(
                VisualEdge(
                    VisualEdgeID(source),
                    VisualEdgeID(target),
                    VisualEdgeType.VIEW,
                )
            )
    if options.highlight_node:
        vg.highlight_ancestors(options.highlight_node)
    return vg


# TODO: Make single dispatch based on node type
def process_node(
    vg: VisualGraph, node: Node, options: VisualGraphOptions
) -> str:
    """
    Returns the contents of a node and add its edges.
    """
    n_id = node.id
    if isinstance(node, ImportNode):
        return node.name
    if isinstance(node, CallNode):
        # The call node body is in struct format to allow pointing to each
        # variable independently
        # https://graphviz.readthedocs.io/en/stable/examples.html#structs-revisited-py
        contents = "<fn> fn"
        vg.edge(
            VisualEdge(
                VisualEdgeID(node.function_id),
                VisualEdgeID(n_id, "fn"),
                VisualEdgeType.FUNCTION,
            )
        )
        if node.positional_args:
            args_contents: List[str] = []
            for i, p_id in enumerate(node.positional_args):
                sub_id = f"p_{i}"
                args_contents.append(f"<{sub_id}> {i}")
                vg.edge(
                    VisualEdge(
                        VisualEdgeID(p_id.id),
                        VisualEdgeID(n_id, sub_id),
                        VisualEdgeType.POSITIONAL_ARG,
                    )
                )
            contents += "| {{" + "|".join(args_contents) + "} | args }"

        if node.keyword_args:
            kwargs_contents: List[str] = []
            for kw in node.keyword_args:
                sub_id = f"k_{kw.key}"
                kwargs_contents.append(f"<{sub_id}> {kw.key}")
                vg.edge(
                    VisualEdge(
                        VisualEdgeID(kw.value),
                        VisualEdgeID(n_id, sub_id),
                        VisualEdgeType.KEYWORD_ARG,
                    )
                )
            contents += "| {{" + "|".join(kwargs_contents) + "} | kwargs }"

        if node.global_reads:
            global_reads_contents: List[str] = []

            for k, v in node.global_reads.items():
                sub_id = f"v_{k}"
                global_reads_contents.append(f"<{sub_id}> {k}")

                vg.edge(
                    VisualEdge(
                        VisualEdgeID(v),
                        VisualEdgeID(n_id, sub_id),
                        VisualEdgeType.GLOBAL_READ,
                    )
                )
            contents += "| {{" + "|".join(global_reads_contents) + "} | vars }"

        if node.implicit_dependencies:
            for ii, im_id in enumerate(node.implicit_dependencies):
                sub_id = f"i_{ii}"
                vg.edge(
                    VisualEdge(
                        VisualEdgeID(im_id),
                        VisualEdgeID(n_id),
                        VisualEdgeType.IMPLICIT_DEPENDENCY,
                    )
                )

        return contents
    if isinstance(node, LiteralNode):
        return repr(node.value)
    if isinstance(node, LookupNode):
        return node.name
    if isinstance(node, MutateNode):
        vg.edge(
            VisualEdge(
                VisualEdgeID(node.source_id),
                VisualEdgeID(n_id, "src"),
                VisualEdgeType.MUTATE_SOURCE,
            )
        )
        vg.edge(
            VisualEdge(
                VisualEdgeID(node.call_id),
                VisualEdgeID(n_id, "call"),
                VisualEdgeType.MUTATE_CALL,
            )
        )
        return "<src> src|<call> call"

    if isinstance(node, GlobalNode):
        vg.edge(
            VisualEdge(
                VisualEdgeID(node.call_id),
                VisualEdgeID(n_id),
                VisualEdgeType.GLOBAL,
            ),
        )
        return node.name


@dataclass
class VisualGraph:
    """
    A visual graph contains a number of nodes and directed edges
    """

    # Make these private and add property lookups so that
    # we are forced to used helper methods to add edges and nodes
    _nodes: List[VisualNode] = field(default_factory=list)
    _edges: List[VisualEdge] = field(default_factory=list)

    # Keep these mappings for more performant traversal, when filtering to highlight ancestors
    # Mapping from each node id to all its parent edges
    _node_id_to_parent_edges: Dict[str, List[VisualEdge]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _node_id_to_node: Dict[str, VisualNode] = field(default_factory=dict)

    @property
    def edges(self) -> Iterable[VisualEdge]:
        return self._edges

    @property
    def nodes(self) -> Iterable[VisualNode]:
        return self._nodes

    def node(self, node: VisualNode) -> None:
        self._nodes.append(node)
        self._node_id_to_node[node.id] = node

    def edge(self, edge: VisualEdge) -> None:
        self._edges.append(edge)
        # If this is a a pointer from source code to next line, don't add it
        # since this doesn't count as a dependency
        if edge.type == VisualEdgeType.NEXT_LINE:
            return
        # Add this edge as a parent edge for the target
        self._node_id_to_parent_edges[edge.target.node_id].append(edge)

    def highlight_ancestors(self, node_id: str) -> None:
        """
        Update a graph to only highlight the ancestors of a certain node.

        We could instead do this graph traversal with the original nodes,
        as we do when computing the program slice. However we have some graph only nodes,
        like the source code, so for now we are re-walking the graph to determine
        the slice at the visual graph level.
        """
        # Set every node to un-highlighted
        for node in self.nodes:
            node.highlighted = False
        for edge in self.edges:
            edge.highlighted = False

        # Traverse the graph, from the node to all its ancestors,
        # every time we encounter a node, set it to highlighted.
        # and then mark it to be traversed.
        frontier = {node_id}
        seen: Set[str] = set()
        while frontier:
            id_ = frontier.pop()
            seen.add(id_)
            self._node_id_to_node[id_].highlighted = True
            for edge in self._node_id_to_parent_edges[id_]:
                edge.highlighted = True
                parent_id = edge.source.node_id
                if parent_id not in seen:
                    frontier.add(parent_id)


def get_node_id(id: str) -> str:
    return id.split(":")[0]


ExtraLabels = List["ExtraLabel"]


@dataclass
class SourceLineType:
    """
    Type used to represent a source code line
    """

    pass


VisualNodeType = Union[NodeType, SourceLineType]


@dataclass
class VisualNode:
    # A unique ID for the node
    id: str
    # The type of the node, used for coloring
    type: VisualNodeType
    # The contents of the cell, either a string for its label
    # or a string in the struct format
    # https://graphviz.readthedocs.io/en/stable/examples.html#structs-revisited-py
    contents: str

    # A list of "extra labels" that are associated with the node
    extra_labels: ExtraLabels

    highlighted: bool = field(default=True)


@dataclass
class ExtraLabel:
    label: str
    type: ExtraLabelType


class ExtraLabelType(Enum):
    VARIABLE = auto()
    ARTIFACT = auto()


@dataclass
class VisualEdge:
    source: VisualEdgeID
    target: VisualEdgeID
    type: VisualEdgeType
    highlighted: bool = field(default=True)


@dataclass
class VisualEdgeID:
    node_id: str
    # The port the edge is related to
    # https://graphviz.org/doc/info/shapes.html#record
    port: Optional[str] = field(default=None)


class VisualEdgeType(Enum):
    """
    A visual edges includes all the possible edges in our DB types,
    as well as the edges we store temporarily to assist in tracing
    """

    # From a function to the node which calls it
    FUNCTION = auto()
    # From a node to the call node that uses it as positional arg
    POSITIONAL_ARG = auto()
    # From a node to the call node that uses it as keyword arg
    KEYWORD_ARG = auto()
    # From a node to a call node which reads it from globals
    GLOBAL_READ = auto()

    # From a source node to the mutate node which represents a mutated
    # version of it
    MUTATE_SOURCE = auto()
    # From a call node to the mutate node which it created for any args it mutated
    MUTATE_CALL = auto()

    # Mapping from a source node to the latest node that they mutate
    LATEST_MUTATE_SOURCE = auto()
    # Mapping from a source node to a node that has a view of it
    VIEW = auto()

    # Edge from a line of source to the next line
    NEXT_LINE = auto()
    # Edge from a line of source to a node that results from it
    SOURCE_CODE = auto()

    # Edge from a node to global node that reads a value from it
    GLOBAL = auto()

    IMPLICIT_DEPENDENCY = auto()
