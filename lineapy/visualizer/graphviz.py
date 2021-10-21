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
    SourceLineType,
    VisualEdgeType,
    VisualGraphOptions,
    VisualNode,
    VisualNodeType,
    tracer_to_visual_graph,
)

NODE_STYLE = {
    # https://graphviz.org/doc/info/colors.html#brewer
    "colorscheme": "pastel19",
}

EDGE_STYLE = {"colorscheme": NODE_STYLE["colorscheme"]}

DEFAULT_EDGE_COLOR = "/greys3/2"
CLUSTER_EDGE_COLOR = "/greys3/3"

ColorableType = Union[NodeType, ExtraLabelType, VisualEdgeType]

# List of types, to use as index to color scheme
# https://graphviz.org/docs/attrs/colorscheme/
TYPES_FOR_COLOR: list[ColorableType] = [
    VisualEdgeType.LATEST_MUTATE_SOURCE,
    VisualEdgeType.VIEW,
    NodeType.CallNode,
    NodeType.LiteralNode,
    NodeType.MutateNode,
    NodeType.ImportNode,
    ExtraLabelType.VARIABLE,
    NodeType.LookupNode,
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
    ExtraLabelType.ARTIFACT: "Artifact Name",
    ExtraLabelType.VARIABLE: "Variable Name",
}

EDGE_TYPE_TO_LABEL: dict[VisualEdgeType, str] = {
    VisualEdgeType.LATEST_MUTATE_SOURCE: "Implied Mutate",
    VisualEdgeType.VIEW: "View",
}

NODE_SHAPES: dict[NodeType, str] = {
    NodeType.CallNode: "record",
    NodeType.LiteralNode: "box",
    NodeType.ImportNode: "box",
    NodeType.LookupNode: "box",
    NodeType.MutateNode: "record",
}

UNDIRECTED_EDGE_TYPES = {
    VisualEdgeType.VIEW,
}


EDGE_STYLES = {
    VisualEdgeType.MUTATE_CALL: "dashed",
    VisualEdgeType.NEXT_LINE: "invis",
}


def get_color(tp: ColorableType) -> str:
    """
    Get the color for a type. Note that graphviz colorscheme indexing
    is 1 based
    """
    return str(TYPES_FOR_COLOR.index(tp) + 1)


def tracer_to_graphviz(
    tracer: Tracer, options: VisualGraphOptions
) -> graphviz.Digraph:
    dot = graphviz.Digraph()

    dot.attr(newrank="true")
    dot.attr("node", **NODE_STYLE)
    dot.attr("edge", **EDGE_STYLE)

    add_legend(dot, options)

    vg = tracer_to_visual_graph(tracer, options)

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
    A single node could have multiple variables and artifacts pointing at it.
    So we make a table with a row for each artifact. Why a table? Well we are putting
    it in the xlabel and a table was an easy way to have multiple rows with different colors.
    """
    rows = [
        f'<TR ><TD BGCOLOR="{get_color(el.type)}"><FONT POINT-SIZE="10">{el.label}</FONT></TD></TR>'
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
    ids to struct pointers: https://graphviz.org/doc/info/shapes.html#record
    """
    if isinstance(pointer, str):
        return pointer
    return ":".join(pointer)


def node_type_to_kwargs(node_type: VisualNodeType) -> dict[str, object]:
    if isinstance(node_type, SourceLineType):
        return {"shape": "plaintext"}
    return {
        "color": get_color(node_type),
        "shape": NODE_SHAPES[node_type],
        "style": "filled",
    }


def edge_type_to_kwargs(edge_type: VisualEdgeType) -> dict[str, object]:
    return {
        "color": get_color(edge_type)
        if edge_type in TYPES_FOR_COLOR
        else DEFAULT_EDGE_COLOR,
        "dir": "none" if edge_type in UNDIRECTED_EDGE_TYPES else "forward",
        "style": EDGE_STYLES.get(edge_type, "solid"),
    }


def add_legend(dot: graphviz.Digraph, options: VisualGraphOptions):
    """
    Add a legend with nodes and edge styles.

    Creates one node for each node style and one edge for each edge style.

    It was difficult to get it to appear in a way that didn't disrupt the  main
    graph. It was easiest to get it to be a vertically aligned column of nodes,
    on the left of the graph. To do this, I link all the nodes with invisible
    edges so they stay vertically alligned.

    https://stackoverflow.com/a/52300532/907060.
    """
    with dot.subgraph(name="cluster_0") as c:
        c.attr(color=CLUSTER_EDGE_COLOR)
        c.attr(label="Legend")

        ##
        # Add nodes to legend
        ##

        # Save the previous ID so we can add an invisible edge.
        prev_id = None
        for node_type, label in NODE_LABELS.items():
            id_ = f"legend_node_{label}"

            extra_labels: ExtraLabels = []
            # If this isn't in the first node, add an invisible edge from
            # the previous node to it.
            if prev_id:
                c.edge(prev_id, id_, style="invis")
            # If this is the first node, add sample extra labels
            else:
                for v, extra_label_label in EXTRA_LABEL_LABELS.items():
                    extra_labels.append(ExtraLabel(extra_label_label, v))
            render_node(
                c,
                VisualNode(id_, node_type, label, extra_labels),
            )
            prev_id = id_

        ##
        # Add edges to legend
        ##

        if options.show_implied_mutations:
            # Keep adding invisible edges, so that all of the nodes are aligned vertically
            id_ = "legend_edge"
            c.node(id_, "", shape="box", style="invis")
            c.edge(prev_id, id_, style="invis")
            prev_id = id_
            for edge_type, label in EDGE_TYPE_TO_LABEL.items():
                id_ = f"legend_edge_{label}"
                # Add invisible nodes, so the edges have something to point to.
                c.node(id_, "", shape="box", style="invis")
                c.edge(
                    prev_id,
                    id_,
                    label=label,
                    **edge_type_to_kwargs(edge_type),
                )
                prev_id = id_
    return id_


def render_node(dot: graphviz.Digraph, node: VisualNode) -> str:
    kwargs = node_type_to_kwargs(node.type)
    if node.extra_labels:
        kwargs["xlabel"] = extra_labels_to_html(node.extra_labels)
    dot.node(node.id, contents_to_label(node.contents), **kwargs)
    return node.id
