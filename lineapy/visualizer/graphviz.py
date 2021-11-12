"""
Functionality to display the tracer as a visual graph.

It first convert it to a graph, using `visual_graph.py`, and then renders
that with graphviz.
"""
from __future__ import annotations

from typing import Optional, Union

import graphviz

from lineapy.data.types import NodeType
from lineapy.visualizer.visual_graph import (
    ExtraLabel,
    ExtraLabels,
    ExtraLabelType,
    SourceLineType,
    VisualEdge,
    VisualEdgeID,
    VisualEdgeType,
    VisualGraphOptions,
    VisualNode,
    VisualNodeType,
    to_visual_graph,
)

GRAPH_STYLE = {"newrank": "true"}

NODE_STYLE: dict[str, str] = {
    # https://graphviz.org/doc/info/colors.html#brewer
    "colorscheme": "pastel19",
}

EDGE_STYLE = {
    "arrowhead": "vee",
    "arrowsize": "0.7",
    "colorscheme": NODE_STYLE["colorscheme"],
}

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
    NodeType.GlobalNode,
]

# Labels for node types for legend
NODE_LABELS: dict[NodeType, str] = {
    NodeType.CallNode: "Call",
    NodeType.LiteralNode: "Literal",
    NodeType.ImportNode: "Import",
    NodeType.LookupNode: "Lookup",
    NodeType.MutateNode: "Mutate",
    NodeType.GlobalNode: "Global",
}


def extra_label_labels(
    options: VisualGraphOptions,
) -> dict[ExtraLabelType, str]:
    """
    Labels for the extra label, to use in the legend,
    """
    l: dict[ExtraLabelType, str] = {}
    if options.show_artifacts:
        l[ExtraLabelType.ARTIFACT] = "Artifact Name"
    if options.show_variables:
        l[ExtraLabelType.VARIABLE] = "Variable Name"
    return l


def edge_labels(
    options: VisualGraphOptions,
) -> dict[VisualEdgeType, str]:
    """
    Labels for the edge types to use in the legend,
    """
    l: dict[VisualEdgeType, str] = {
        VisualEdgeType.SOURCE_CODE: "Source Code",
        VisualEdgeType.MUTATE_CALL: "Mutate Call",
        VisualEdgeType.IMPLICIT_DEPENDENCY: "Implicit Dependency",
    }
    if options.show_implied_mutations:
        l[VisualEdgeType.LATEST_MUTATE_SOURCE] = "Implied Mutate"
    if options.show_views:
        l[VisualEdgeType.VIEW] = "View"
    return l


NODE_SHAPES: dict[NodeType, str] = {
    NodeType.CallNode: "record",
    NodeType.LiteralNode: "box",
    NodeType.ImportNode: "box",
    NodeType.LookupNode: "box",
    NodeType.MutateNode: "record",
    NodeType.GlobalNode: "box",
}

UNDIRECTED_EDGE_TYPES = {
    VisualEdgeType.VIEW,
}


EDGE_STYLES = {
    VisualEdgeType.MUTATE_CALL: "dashed",
    VisualEdgeType.NEXT_LINE: "invis",
    VisualEdgeType.SOURCE_CODE: "dotted",
    VisualEdgeType.IMPLICIT_DEPENDENCY: "bold",
}


def get_color(tp: ColorableType) -> str:
    """
    Get the color for a type. Note that graphviz colorscheme indexing
    is 1 based
    """
    try:
        return str(TYPES_FOR_COLOR.index(tp) + 1)
    except ValueError:
        return "/greys3/1"


def to_graphviz(options: VisualGraphOptions) -> graphviz.Digraph:
    dot = graphviz.Digraph(node_attr=NODE_STYLE, edge_attr=EDGE_STYLE)
    dot.attr(**GRAPH_STYLE)

    add_legend(dot, options)

    vg = to_visual_graph(options)

    for node in vg.nodes:
        render_node(dot, node)

    for edge in vg.edges:
        render_edge(dot, edge)

    return dot


def render_edge(dot, edge: VisualEdge) -> None:
    if not edge.highlighted:
        return
    dot.edge(
        edge_id_to_str(edge.source),
        edge_id_to_str(edge.target),
        **edge_type_to_kwargs(edge.type),
    )


def edge_id_to_str(edge_id: VisualEdgeID) -> str:
    if edge_id.port is not None:
        return f"{edge_id.node_id}:{edge_id.port}"
    return edge_id.node_id


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
        prev_id: Optional[str] = None
        for node_type, label in NODE_LABELS.items():
            id_ = f"legend_node_{label}"

            extra_labels: ExtraLabels = []
            # If this isn't in the first node, add an invisible edge from
            # the previous node to it.
            if prev_id:
                c.edge(prev_id, id_, style="invis")
            # If this is the first node, add sample extra labels
            else:
                for v, extra_label_label in extra_label_labels(
                    options
                ).items():
                    extra_labels.append(ExtraLabel(extra_label_label, v))
            render_node(
                c,
                VisualNode(id_, node_type, label, extra_labels),
            )
            prev_id = id_

        ##
        # Add edges to legend
        ##
        edges_for_legend = edge_labels(options)
        if edges_for_legend:
            # Keep adding invisible edges, so that all of the nodes are aligned vertically
            id_ = "legend_edge"
            c.node(id_, "", shape="box", style="invis")
            c.edge(prev_id, id_, style="invis")
            prev_id = id_
            for edge_type, label in edges_for_legend.items():
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


def render_node(dot: graphviz.Digraph, node: VisualNode) -> None:
    if not node.highlighted:
        return
    kwargs = node_type_to_kwargs(node.type)
    if node.extra_labels:
        kwargs["xlabel"] = extra_labels_to_html(node.extra_labels)
    dot.node(node.id, node.contents, **kwargs)
