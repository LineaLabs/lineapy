"""
Functionality to display the tracer as a visual graph.

It first convert it to a graph, using `visual_graph.py`, and then renders
that with graphviz.
"""
from __future__ import annotations

from collections import defaultdict
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

SERIF_FONT = "Helvetica"
MONOSPACE_FONT = "Courier"

GRAPH_STYLE = {
    "newrank": "true",
    "splines": "polyline",
    "fontname": SERIF_FONT,
}

NODE_STYLE: dict[str, str] = {
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

# We use the Vega Category 20 color scheme since it provides dark and light version
# of 10 colors, which we can use for node values to show which are highlighted.
# https://vega.github.io/vega/docs/schemes/#category20
# We also give them all names for easier access

# Represents a pair of colors, to toggle between highlighted and not highlighted
Colors = tuple[str, str]


VEGA_CATEGORY_20: dict[str, Colors] = {
    "blue": (
        "#1f77b4",
        "#aec7e8",
    ),
    "orange": (
        "#ff7f0e",
        "#ffbb78",
    ),
    "green": (
        "#2ca02c",
        "#98df8a",
    ),
    "red": (
        "#d62728",
        "#ff9896",
    ),
    "purple": (
        "#9467bd",
        "#c5b0d5",
    ),
    "brown": (
        "#8c564b",
        "#c49c94",
    ),
    "pink": (
        "#e377c2",
        "#f7b6d2",
    ),
    "grey": (
        "#7f7f7f",
        "#c7c7c7",
    ),
    "yellow": (
        "#bcbd22",
        "#dbdb8d",
    ),
    "aqua": (
        "#17becf",
        "#9edae5",
    ),
}
ALPHA = 50
alpha_hex = hex(ALPHA)[2:]
# Alpha fraction from 0 to 255 to apply to lighten the second colors
# Make all the secondary colors lighter, by applying an alpha
# Graphviz takes this as an alpha value in hex form
# https://graphviz.org/docs/attr-types/color/
for name, colors in VEGA_CATEGORY_20.items():
    primary, secondary = colors
    lightened_secondary = secondary + alpha_hex
    VEGA_CATEGORY_20[name] = (primary, lightened_secondary)

BORDER_COLOR = VEGA_CATEGORY_20["grey"]
BLACK = "#000000"
FONT_COLOR = (BLACK, BLACK + alpha_hex)

CLUSTER_EDGE_COLOR = VEGA_CATEGORY_20["grey"][0]


ColorableType = Union[NodeType, ExtraLabelType, VisualEdgeType]


# Mapping of each node type to its colors
COLORS: dict[ColorableType, Colors] = defaultdict(
    lambda: VEGA_CATEGORY_20["grey"],
    {
        NodeType.CallNode: VEGA_CATEGORY_20["pink"],
        NodeType.LiteralNode: VEGA_CATEGORY_20["green"],
        NodeType.MutateNode: VEGA_CATEGORY_20["red"],
        NodeType.ImportNode: VEGA_CATEGORY_20["purple"],
        NodeType.LookupNode: VEGA_CATEGORY_20["yellow"],
        # Make the global node and variables same color, since both are about variables
        NodeType.GlobalNode: VEGA_CATEGORY_20["brown"],
        ExtraLabelType.VARIABLE: VEGA_CATEGORY_20["aqua"],
        ExtraLabelType.ARTIFACT: VEGA_CATEGORY_20["orange"],
        # Make same color as mutate node
        VisualEdgeType.LATEST_MUTATE_SOURCE: VEGA_CATEGORY_20["red"],
        VisualEdgeType.VIEW: VEGA_CATEGORY_20["aqua"],
    },
)

# Labels for node types for legend
NODE_LABELS: dict[NodeType, str] = {
    NodeType.CallNode: "Call",
    NodeType.LiteralNode: "Literal",
    NodeType.ImportNode: "Import",
    NodeType.LookupNode: "Lookup",
    NodeType.MutateNode: "Mutate",
    NodeType.GlobalNode: "Global",
}


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


def get_color(tp: ColorableType, is_highlighted: bool) -> str:
    """
    Get the color for a type. Note that graphviz colorscheme indexing
    is 1 based
    """
    return COLORS[tp][not is_highlighted]


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
) -> dict[str, object]:
    if isinstance(node_type, SourceLineType):
        return {
            "shape": "text",
            "fontcolor": FONT_COLOR[not highlighted],
            # Remove node edge
            "penwidth": "0",
        }
    return {
        "fillcolor": get_color(node_type, highlighted),
        "shape": NODE_SHAPES[node_type],
        "color": BORDER_COLOR[not highlighted],
        "fontcolor": FONT_COLOR[not highlighted],
        "style": "filled",
    }


def edge_type_to_kwargs(
    edge_type: VisualEdgeType, highlighted: bool
) -> dict[str, object]:
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
