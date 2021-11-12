from __future__ import annotations

from dataclasses import InitVar, dataclass, field

import graphviz
from IPython.display import SVG, DisplayObject

from lineapy.data.graph import Graph
from lineapy.instrumentation.tracer import Tracer
from lineapy.visualizer.graphviz import to_graphviz
from lineapy.visualizer.visual_graph import VisualGraphOptions


@dataclass
class Visualizer:
    """
    Stores a rendered graphviz digraph. Has helper classmethods to use
    for construction, as well as methods for output as different useful
    formats.
    """

    options: InitVar[VisualGraphOptions]
    digraph: graphviz.Digraph = field(init=False)

    def __post_init__(self, options: VisualGraphOptions):
        self.digraph = to_graphviz(options)

    def render_pdf_file(self, filename: str = "tracer") -> None:
        """
        Renders a PDF file for the graph and tries to open it.
        """
        self.digraph.render(filename, view=True, format="pdf", quiet=True)

    def render_svg(self) -> str:
        return self.digraph.pipe(format="svg", quiet=True).decode()

    def ipython_display_object(self) -> DisplayObject:
        return SVG(self.render_svg())

    @classmethod
    def for_test_snapshot(cls, tracer: Tracer) -> Visualizer:
        """
        Create a graph for saving as a snapshot, to help with visual diffs in PRs.
        """
        options = VisualGraphOptions(
            tracer.graph,
            tracer,
            highlight_node=None,
            # This is genenerally repetative, and we can avoid it.
            show_implied_mutations=False,
            # Views are too verbose to show in the test output
            show_views=False,
            show_code=True,
            show_artifacts=True,
            show_variables=True,
        )
        return cls(options)

    @classmethod
    def for_test_cli(cls, tracer: Tracer) -> Visualizer:
        """
        Create a graph to use when visualizing after passing in `--visualize`
        during testing.

        Show as much as we can for debugging.
        """
        options = VisualGraphOptions(
            tracer.graph,
            tracer,
            highlight_node=None,
            show_implied_mutations=True,
            show_views=True,
            show_code=True,
            show_artifacts=True,
            show_variables=True,
        )
        return cls(options)

    @classmethod
    def for_public(cls, tracer: Tracer) -> Visualizer:
        """
        Create a graph for our public API, when showing the whole graph.
        """
        options = VisualGraphOptions(
            tracer.graph,
            tracer,
            highlight_node=None,
            show_implied_mutations=False,
            show_views=False,
            show_code=True,
            show_artifacts=True,
            show_variables=False,
        )
        return cls(options)

    @classmethod
    def for_public_node(cls, graph: Graph, node_id: str) -> Visualizer:
        """
        Create a graph for our public API, when showing a single node.

        Note: The tracer won't be passed in this case, since it is happening
        inside the executor and we don't have access to the tracer.
        """
        options = VisualGraphOptions(
            graph,
            tracer=None,
            highlight_node=node_id,
            show_implied_mutations=False,
            show_views=False,
            show_code=True,
            show_artifacts=False,
            show_variables=False,
        )

        return cls(options)
