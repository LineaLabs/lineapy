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

    # Whether to show edges for the state the tracer keeps about view
    # and mutation tracking
    show_view_and_mutation_tracking: bool = field(default=False)


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
        contents, edges = contents_and_edges(node)
        vg.edges.extend(edges)
        vg.nodes.append(
            VisualNode(node.id, node.node_type, contents, extra_labels)
        )

    # Then we can add all the additional information from the tracer
    if options.show_view_and_mutation_tracking:
        # the mutate nodes
        for source, mutate in tracer.source_to_mutate.items():
            vg.edges.append(
                VisualEdge(source, mutate, VisualEdgeType.LATEST_MUTATE_SOURCE)
            )

        # Create a set of unique pairs of viewers, where order doesn't matter
        # Since they aren't directed
        viewer_pairs: set[frozenset[LineaID]] = {
            frozenset([source, viewer])
            for source, viewers in tracer.viewers.items()
            for viewer in viewers
        }
        # for source, target in viewer_pairs:
        #     vg.edges.append(VisualEdge(source, target, VisualEdgeType.VIEW))
    return vg


def contents_and_edges(node: Node) -> tuple[Contents, list[VisualEdge]]:
    """
    Get the contents and a list of edges from the node, depending on its type
    """
    n_id = node.id
    if isinstance(node, ImportNode):
        return node.library.name, []
    if isinstance(node, CallNode):
        contents: list[tuple[str, str]] = [("fn", "fn")]
        edges: list[VisualEdge] = [
            VisualEdge(node.function_id, (n_id, "fn"), VisualEdgeType.FUNCTION)
        ]
        for i, a_id in enumerate(node.positional_args):
            sub_id = f"positional_{i}"
            contents.append((sub_id, str(i)))
            edges.append(
                VisualEdge(a_id, (n_id, sub_id), VisualEdgeType.POSITIONAL_ARG)
            )
        for k, a_id in node.keyword_args.items():
            sub_id = f"keyword_{k}"
            contents.append((sub_id, k))
            edges.append(
                VisualEdge(a_id, (n_id, sub_id), VisualEdgeType.KEYWORD_ARG)
            )

        return contents, edges
    if isinstance(node, LiteralNode):
        return repr(node.value), []
    if isinstance(node, LookupNode):
        return node.name, []
    if isinstance(node, MutateNode):
        contents = [("src", "src"), ("call", "call")]
        edges = [
            VisualEdge(
                node.source_id,
                (n_id, "src"),
                VisualEdgeType.MUTATE_SOURCE,
            ),
            VisualEdge(
                node.call_id,
                (n_id, "call"),
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


Contents = Union[str, list[tuple[str, str]]]
ExtraLabels = list["ExtraLabel"]


@dataclass
class VisualNode:
    # A unique ID for the node
    id: str
    # The type of the node, used for coloring
    type: NodeType
    # Either a label, or a list of tuples corresponding to sub_id, label
    # for it as a "struct"
    contents: Contents

    # A list of "extra labels" that are associated with the node
    extra_labels: ExtraLabels


@dataclass
class ExtraLabel:
    label: str
    type: ExtraLabelType


class ExtraLabelType(Enum):
    VARIABLE = auto()
    ARTIFACT = auto()


# Either a string pointing to another node, or a pair of strings, the first
# representing the id of another node, and the second the id of its sub part
Pointer = Union[str, tuple[str, str]]


@dataclass
class VisualEdge:
    source: Pointer
    target: Pointer
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

    # From a source node to the mutate node which represents a mutated
    # version of it
    MUTATE_SOURCE = auto()
    # From a call node to the mutate node which it created for any args it mutated
    MUTATE_CALL = auto()

    # Mapping from a source node to the latest node that they mutate
    LATEST_MUTATE_SOURCE = auto()
    # Mapping from a source node to a node that has a view of it
    VIEW = auto()
