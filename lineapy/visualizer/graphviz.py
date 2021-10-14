"""
Functionality to display the tracer as a visual graph.

It first convert it to a graph, using `visual_graph.py`, and then renders
that with graphviz.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Union

import graphviz

from lineapy.data.types import NodeType

if TYPE_CHECKING:
    from lineapy.instrumentation.tracer import Tracer

from lineapy.visualizer.visual_graph import (
    Contents,
    ExtraLabel,
    ExtraLabels,
    ExtraLabelType,
    Pointer,
    VisualEdgeType,
    VisualNode,
    tracer_to_visual_graph,
)

NODE_STYLE = {
    # https://graphviz.org/doc/info/colors.html#brewer
    "colorscheme": "pastel19",
    "style": "filled",
}

EDGE_STYLE = {"colorscheme": NODE_STYLE["colorscheme"]}

ColorableType = Union[NodeType, ExtraLabelType, VisualEdgeType]

# List of types, to use as index to color scheme
# https://graphviz.org/docs/attrs/colorscheme/
TYPES_FOR_COLOR: list[ColorableType] = [
    VisualEdgeType.LATEST_MUTATE_SOURCE,
    VisualEdgeType.VIEW,
    NodeType.CallNode,
    NodeType.LiteralNode,
    NodeType.ImportNode,
    NodeType.LookupNode,
    NodeType.MutateNode,
    ExtraLabelType.VARIABLE,
    ExtraLabelType.ARTIFACT,
]

# Labels for node types for legend
NODE_LABELS: dict[NodeType, str] = {
    NodeType.CallNode: "Call",
    NodeType.LiteralNode: "Literal",
    NodeType.ImportNode: "Import",
    NodeType.LookupNode: "Lookup",
    NodeType.MutateNode: "Mutate",
}

EXTRA_LABEL_LABELS: dict[ExtraLabelType, str] = {
    ExtraLabelType.ARTIFACT: "Artifact",
    ExtraLabelType.VARIABLE: "Variable",
}

EDGE_TYPE_TO_LABEL: dict[VisualEdgeType, str] = {
    VisualEdgeType.LATEST_MUTATE_SOURCE: "Latest Mutate",
    VisualEdgeType.VIEW: "View",
}

NODE_SHAPES: dict[NodeType, str] = {
    NodeType.CallNode: "record",
    NodeType.LiteralNode: "box",
    NodeType.ImportNode: "box",
    NodeType.LookupNode: "box",
    NodeType.MutateNode: "record",
}


def get_color(tp: ColorableType) -> str:
    """
    Get the color for a type. Note that graphviz colorscheme indexing
    is 1 based
    """
    return str(TYPES_FOR_COLOR.index(tp) + 1)


def tracer_to_graphviz(tracer: Tracer) -> graphviz.Digraph:
    dot = graphviz.Digraph()
    dot.attr("node", **NODE_STYLE)
    dot.attr("edge", **EDGE_STYLE)
    add_legend(dot)

    vg = tracer_to_visual_graph(tracer)
    for node in vg.nodes:
        render_node(dot, node)
    for edge in vg.edges:
        dot.edge(
            pointer_to_id(edge.source),
            pointer_to_id(edge.target),
            **edge_type_to_kwargs(edge.type),
        )
    return dot


def extra_labels_to_html(extra_labels: ExtraLabels) -> str:
    """
    Convert extra labels into an HTML table, where each label is a row.
    """
    rows = [
        f'<TR><TD BGCOLOR="{get_color(el.type)}"><FONT POINT-SIZE="10">{el.label}</FONT></TD></TR>'
        for el in extra_labels
    ]
    return f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">{"".join(rows)}</TABLE>>'


def contents_to_label(contents: Contents) -> str:
    """
    Converts a contents into a label, mapping nested contents into records.
    """
    if isinstance(contents, str):
        return contents
    # https://graphviz.readthedocs.io/en/stable/examples.html#structs-revisited-py
    return "|".join(f"<{id_}> {label}" for id_, label in contents)


def pointer_to_id(pointer: Pointer) -> str:
    """
    Maps from a pointer to a graphviz id to use in an edge, mapping nested
    ids to struct pointers
    """
    if isinstance(pointer, str):
        return pointer
    return ":".join(pointer)


def node_type_to_kwargs(node_type: NodeType) -> dict[str, object]:
    return {
        "color": get_color(node_type),
        "shape": NODE_SHAPES[node_type],
    }


def edge_type_to_kwargs(edge_type: VisualEdgeType) -> dict[str, object]:
    return {
        "color": get_color(edge_type) if edge_type in TYPES_FOR_COLOR else None
    }


def add_legend(dot: graphviz.Digraph) -> None:
    """
    Add a legend with nodes and edge styles

    https://stackoverflow.com/a/52300532/907060
    """
    with dot.subgraph(name="cluster_0") as c:
        c.attr(label="Legend")
        prev_id = None

        edge_label_items = iter(EDGE_TYPE_TO_LABEL.items())
        for node_type, label in NODE_LABELS.items():
            id_ = f"legend_{label}"

            extra_labels: ExtraLabels = []
            # Add sample edges for the different types of edges
            # Once we are done, make them invsible, so that nodes are still all aligned
            if prev_id:
                try:
                    edge_type, label = next(edge_label_items)
                    kwargs = edge_type_to_kwargs(edge_type)
                    kwargs["label"] = label
                except StopIteration:
                    kwargs = {"style": "invis"}
                c.edge(prev_id, id_, **kwargs)
            # If this is the first node, add sample extra labels
            else:
                for v, label in EXTRA_LABEL_LABELS.items():
                    extra_labels.append(ExtraLabel(label, v))
            render_node(
                c,
                VisualNode(id_, node_type, label, extra_labels),
            )
            prev_id = id_


def render_node(dot: graphviz.Digraph, node: VisualNode) -> None:
    kwargs = node_type_to_kwargs(node.type)
    if node.extra_labels:
        kwargs["xlabel"] = extra_labels_to_html(node.extra_labels)
    dot.node(node.id, contents_to_label(node.contents), **kwargs)
