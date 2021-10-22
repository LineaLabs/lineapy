"""
An abstract graph representation that is conducive to being visualized easily.

We include in this graph:

* From the DB about this session:
  * Nodes
  * Artifacts
* From the tracer:
  * Mutation and view edges
  * Variables

We currently don't include, but could:

* Node values
* Source code
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Union

from lineapy.data.types import (
    CallNode,
    ImportNode,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
    NodeType,
)

if TYPE_CHECKING:
    from lineapy.instrumentation.tracer import Tracer


@dataclass
class VisualGraphOptions:
    """
    Class to store options for the visualizer, so that we can properly type them
    as we pass this down the stack.

    It would be nice if we could just use keyword arguments, and type this directly.

    We can't use a TypedDict on **kwargs (see https://www.python.org/dev/peps/pep-0589/#rejected-alternatives)
    In Python 3.10 we can maybe use https://www.python.org/dev/peps/pep-0612/.
    """

    # Whether to add edges for the implied views in the tracer
    show_implied_mutations: bool = field(default=False)

    # Whether to add edges for the views kept in the tracer
    show_views: bool = field(default=False)

    # Whether to show source code in the graph
    show_code: bool = field(default=True)

    # Whether to add edges for global variable reads in calls
    show_global_reads: bool = field(default=True)


def tracer_to_visual_graph(
    tracer: Tracer, options: VisualGraphOptions
) -> VisualGraph:
    vg = VisualGraph()

    # We will create some mappings to start, so that we can add the
    # variables and artifacts to each node

    # First create a mapping of each node ID to all of its artifact names
    id_to_artifacts: dict[str, list[Optional[str]]] = defaultdict(list)
    for a in tracer.session_artifacts():
        id_to_artifacts[a.id].append(a.name)

    # Then create a mapping of each node to the variables which point to it
    id_to_variables: dict[str, list[str]] = defaultdict(list)
    for name, node in tracer.variable_name_to_node.items():
        id_to_variables[node.id].append(name)

    # First add all the nodes from the session
    for node in tracer.graph.nodes:
        extra_labels = [
            ExtraLabel(a or "Unnamed Artifact", ExtraLabelType.ARTIFACT)
            for a in id_to_artifacts[node.id]
        ] + [
            ExtraLabel(v, ExtraLabelType.VARIABLE)
            for v in id_to_variables[node.id]
        ]
        contents, edges = contents_and_edges(node, options)
        vg.edges.extend(edges)
        vg.nodes.append(
            VisualNode(node.id, node.node_type, contents, extra_labels)
        )

    # For now, our algorithm for making nodes based on source locations is:
    # 1. Whenever we encounter a node, if we havent made a source code node
    #    for that pair of start and end lines, make one and add an edge
    #    from the previous to it.
    # 2. We add an edge from that source node to the node.

    # This assumes that we iterate through nodes in line order, and that
    #  we skip printing any lines that don't appear in nodes.
    # It also assumes that we have no overlapping line number ranges,
    # i.e. a node that is from lines 1-3 and another node just on line 3
    # If this doesn occur, we will end up print line 3's source code twice.

    added_source_ids: set[str] = set()
    last_added_source_id: Optional[str] = None

    # Then add the source code nodes
    for n in tracer.graph.nodes:
        source_location = n.source_location
        if not source_location:
            continue
        id_ = f"{source_location.source_code.id}-{source_location.lineno}-{source_location.end_lineno}"
        if id_ not in added_source_ids:
            added_source_ids.add(id_)
            contents = "\n".join(
                source_location.source_code.code.splitlines()[
                    source_location.lineno - 1 : source_location.end_lineno
                ]
            )
            vg.nodes.append(VisualNode(id_, SourceLineType(), contents, []))

            if last_added_source_id:
                vg.edges.append(
                    VisualEdge(
                        last_added_source_id,
                        id_,
                        VisualEdgeType.NEXT_LINE,
                    )
                )
            last_added_source_id = id_
        vg.edges.append(
            VisualEdge(
                id_,
                n.id,
                VisualEdgeType.SOURCE_CODE,
            )
        )
    # Then we can add all the additional information from the tracer
    if options.show_implied_mutations:
        # the mutate nodes
        for source, mutate in tracer.source_to_mutate.items():
            vg.edges.append(
                VisualEdge(source, mutate, VisualEdgeType.LATEST_MUTATE_SOURCE)
            )

    if options.show_views:
        # Create a set of unique pairs of viewers, where order doesn't matter
        # Since they aren't directed
        viewer_pairs: set[frozenset[LineaID]] = {
            frozenset([source, viewer])
            for source, viewers in tracer.viewers.items()
            for viewer in viewers
        }
        for source, target in viewer_pairs:
            vg.edges.append(VisualEdge(source, target, VisualEdgeType.VIEW))
    return vg


def contents_and_edges(
    node: Node, options: VisualGraphOptions
) -> tuple[str, list[VisualEdge]]:
    """
    Get the contents and a list of edges from the node, depending on its type
    """
    n_id = node.id
    if isinstance(node, ImportNode):
        return node.library.name, []
    if isinstance(node, CallNode):
        # The call node body is in struct format to allow pointing to each
        # variable independently
        # https://graphviz.readthedocs.io/en/stable/examples.html#structs-revisited-py
        contents = "<fn> fn"
        edges: list[VisualEdge] = [
            VisualEdge(node.function_id, f"{n_id}:fn", VisualEdgeType.FUNCTION)
        ]
        if node.positional_args:
            args_contents: list[str] = []
            for i, a_id in enumerate(node.positional_args):
                sub_id = f"p_{i}"
                args_contents.append(f"<{sub_id}> {i}")
                edges.append(
                    VisualEdge(
                        a_id, f"{n_id}:{sub_id}", VisualEdgeType.POSITIONAL_ARG
                    )
                )
            contents += "| {{" + "|".join(args_contents) + "} | args }"

        if node.keyword_args:
            kwargs_contents: list[str] = []
            for k, a_id in node.keyword_args.items():
                sub_id = f"k_{k}"
                kwargs_contents.append(f"<{sub_id}> {k}")
                edges.append(
                    VisualEdge(
                        a_id, f"{n_id}:{sub_id}", VisualEdgeType.KEYWORD_ARG
                    )
                )
            contents += "| {{" + "|".join(kwargs_contents) + "} | kwargs }"

        if options.show_global_reads and node.global_reads:
            global_reads_contents: list[str] = []

            for k, v in node.global_reads.items():
                sub_id = f"v_{k}"
                global_reads_contents.append(f"<{sub_id}> {k}")

                edges.append(
                    VisualEdge(
                        v, f"{n_id}:{sub_id}", VisualEdgeType.GLOBAL_READ
                    )
                )
            contents += "| {{" + "|".join(global_reads_contents) + "} | vars }"

        return contents, edges
    if isinstance(node, LiteralNode):
        return repr(node.value), []
    if isinstance(node, LookupNode):
        return node.name, []
    if isinstance(node, MutateNode):
        contents = "<src> src|<call> call"
        edges = [
            VisualEdge(
                node.source_id,
                f"{n_id}:src",
                VisualEdgeType.MUTATE_SOURCE,
            ),
            VisualEdge(
                node.call_id,
                f"{n_id}:call",
                VisualEdgeType.MUTATE_CALL,
            ),
        ]
        return contents, edges


@dataclass
class VisualGraph:
    """
    A visual graph contains a number of nodes and directed edges
    """

    nodes: list[VisualNode] = field(default_factory=list)
    edges: list[VisualEdge] = field(default_factory=list)


ExtraLabels = list["ExtraLabel"]


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


@dataclass
class ExtraLabel:
    label: str
    type: ExtraLabelType


class ExtraLabelType(Enum):
    VARIABLE = auto()
    ARTIFACT = auto()


@dataclass
class VisualEdge:
    source: str
    target: str
    type: VisualEdgeType


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
