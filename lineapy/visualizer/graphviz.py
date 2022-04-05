"""
Functionality to display the tracer as a visual graph.

It first convert it to a graph, using `visual_graph.py`, and then renders
that with graphviz.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Optional, Union

try:
    import graphviz
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "graphviz is not installed, please install graphviz in your local environment to visualize artifacts"
    ) from None

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

SERIF_FONT = "Helvetica"
MONOSPACE_FONT = "Courier"

GRAPH_STYLE = {
    "newrank": "true",
    "splines": "polyline",
    "fontname": SERIF_FONT,
}

NODE_STYLE: Dict[str, str] = {
    "width": "0",
    "height": "0",
    # in inches
    "margin": "0.04",
    "penwidth": "0",
    "fontsize": "11",
    "fontname": MONOSPACE_FONT,
}

EDGE_STYLE = {
    "arrowhead": "vee",
    "arrowsize": "0.5",
    "fontsize": "9",
    "fontname": SERIF_FONT,
}


# Copied from pastel19 on
# https://graphviz.org/doc/info/colors.html so we can add transparency
BREWER_PASTEL: Dict[str, str] = {
    "red": "#fbb4ae",
    "blue": "#b3cde3",
    "green": "#ccebc5",
    "purple": "#decbe4",
    "orange": "#fed9a6",
    "yellow": "#ffffcc",
    "brown": "#e5d8bd",
    "pink": "#fddaec",
    "grey": "#f2f2f2",
}
ALPHA = 60
# Alpha fraction from 0 to 255 to apply to lighten the second colors
# Make all the secondary colors lighter, by applying an alpha
# Graphviz takes this as an alpha value in hex form
# https://graphviz.org/docs/attr-types/color/
alpha_hex = hex(ALPHA)[2:]


def color(original_color: str, highlighted: bool) -> str:
    if highlighted:
        return original_color
    # If not highlighted, make it more transparent
    return original_color + alpha_hex


BORDER_COLOR = BREWER_PASTEL["grey"]
FONT_COLOR = "#000000"

CLUSTER_EDGE_COLOR = BREWER_PASTEL["grey"]


ColorableType = Union[NodeType, ExtraLabelType, VisualEdgeType]


# Mapping of each node type to its color
COLORS: Dict[ColorableType, str] = defaultdict(
    lambda: "#d4d4d4",  # use a slightly darker grey by default
    {
        NodeType.CallNode: BREWER_PASTEL["pink"],
        NodeType.LiteralNode: BREWER_PASTEL["green"],
        NodeType.MutateNode: BREWER_PASTEL["red"],
        NodeType.ImportNode: BREWER_PASTEL["purple"],
        NodeType.LookupNode: BREWER_PASTEL["yellow"],
        # Make the global node and variables same color, since both are about variables
        NodeType.GlobalNode: BREWER_PASTEL["brown"],
        ExtraLabelType.VARIABLE: BREWER_PASTEL["brown"],
        ExtraLabelType.ARTIFACT: BREWER_PASTEL["orange"],
        # Make same color as mutate node
        VisualEdgeType.LATEST_MUTATE_SOURCE: BREWER_PASTEL["red"],
        VisualEdgeType.VIEW: BREWER_PASTEL["blue"],
    },
)

# Labels for node types for legend
NODE_LABELS: Dict[NodeType, str] = {
    NodeType.CallNode: "Call",
    NodeType.LiteralNode: "Literal",
    NodeType.ImportNode: "Import",
    NodeType.LookupNode: "Lookup",
    NodeType.MutateNode: "Mutate",
    NodeType.GlobalNode: "Global",
}


NODE_SHAPES: Dict[NodeType, str] = {
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


EDGE_STYLES = defaultdict(
    lambda: "solid",
    {
        VisualEdgeType.MUTATE_CALL: "dashed",
        VisualEdgeType.NEXT_LINE: "invis",
        VisualEdgeType.SOURCE_CODE: "dotted",
        VisualEdgeType.IMPLICIT_DEPENDENCY: "bold",
    },
)


def extra_label_labels(
    options: VisualGraphOptions,
) -> Dict[ExtraLabelType, str]:
    """
    Labels for the extra label, to use in the legend,
    """
    l: Dict[ExtraLabelType, str] = {}
    if options.show_artifacts:
        l[ExtraLabelType.ARTIFACT] = "Artifact Name"
    if options.show_variables:
        l[ExtraLabelType.VARIABLE] = "Variable Name"
    return l


def edge_labels(
    options: VisualGraphOptions,
) -> Dict[VisualEdgeType, str]:
    """
    Labels for the edge types to use in the legend,
    """
    l: Dict[VisualEdgeType, str] = {
        VisualEdgeType.SOURCE_CODE: "Source Code",
        VisualEdgeType.MUTATE_CALL: "Mutate Call",
        VisualEdgeType.IMPLICIT_DEPENDENCY: "Implicit Dependency",
    }
    if options.show_implied_mutations:
        l[VisualEdgeType.LATEST_MUTATE_SOURCE] = "Implied Mutate"
    if options.show_views:
        l[VisualEdgeType.VIEW] = "View"
    return l


def get_color(tp: ColorableType, highlighted: bool) -> str:
    """
    Get the color for a type. Note that graphviz colorscheme indexing
    is 1 based
    """
    return color(COLORS[tp], highlighted)


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
    dot.edge(
        edge_id_to_str(edge.source),
        edge_id_to_str(edge.target),
        **edge_type_to_kwargs(edge.type, edge.highlighted),
    )


def edge_id_to_str(edge_id: VisualEdgeID) -> str:
    if edge_id.port is not None:
        return f"{edge_id.node_id}:{edge_id.port}"
    return edge_id.node_id


def extra_labels_to_html(extra_labels: ExtraLabels, highlighted: bool) -> str:
    """
    Convert extra labels into an HTML table, where each label is a row.
    A single node could have multiple variables and artifacts pointing at it.
    So we make a table with a row for each artifact. Why a table? Well we are putting
    it in the xlabel and a table was an easy way to have multiple rows with different colors.
    """
    rows = [
        f'<TR ><TD BGCOLOR="{get_color(el.type, highlighted)}"><FONT POINT-SIZE="10">{el.label}</FONT></TD></TR>'
        for el in extra_labels
    ]
    return f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">{"".join(rows)}</TABLE>>'


def node_type_to_kwargs(
    node_type: VisualNodeType, highlighted: bool
) -> Dict[str, object]:
    if isinstance(node_type, SourceLineType):
        return {
            "shape": "plaintext",
            "fontcolor": color(FONT_COLOR, highlighted),
        }
    return {
        "fillcolor": get_color(node_type, highlighted),
        "shape": NODE_SHAPES[node_type],
        "color": color(BORDER_COLOR, highlighted),
        "fontcolor": color(FONT_COLOR, highlighted),
        "style": "filled",
    }


def edge_type_to_kwargs(
    edge_type: VisualEdgeType, highlighted: bool
) -> Dict[str, object]:
    return {
        "color": f"{get_color(edge_type, highlighted)}",
        "dir": "none" if edge_type in UNDIRECTED_EDGE_TYPES else "forward",
        "style": EDGE_STYLES[edge_type],
    }


def add_legend(dot: graphviz.Digraph, options: VisualGraphOptions):
    """
    Add a legend with nodes and edge styles.

    Creates one node for each node style and one edge for each edge style.

    It was difficult to get it to appear in a way that didn't disrupt the  main
    graph. It was easiest to get it to be a vertically aligned column of nodes,
    on the left of the graph. To do this, I link all the nodes with invisible
    edges so they stay vertically aligned.

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
                fontname=SERIF_FONT,
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
                    **edge_type_to_kwargs(edge_type, highlighted=True),
                )
                prev_id = id_
    return id_


def render_node(
    dot: graphviz.Digraph, node: VisualNode, **overrides: str
) -> None:
    kwargs = node_type_to_kwargs(node.type, node.highlighted)
    if node.extra_labels:
        kwargs["xlabel"] = extra_labels_to_html(
            node.extra_labels, node.highlighted
        )
    kwargs.update(overrides)
    dot.node(node.id, node.contents, **kwargs)
