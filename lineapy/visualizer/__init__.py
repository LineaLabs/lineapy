from __future__ import annotations

from dataclasses import InitVar, dataclass, field

try:
    import graphviz
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "graphviz is not installed, please install graphviz in your local environment to visualize artifacts"
    ) from None

from IPython.display import HTML, DisplayObject

from lineapy.data.graph import Graph
from lineapy.instrumentation.tracer import Tracer
from lineapy.visualizer.graphviz import to_graphviz
from lineapy.visualizer.optimize_svg import optimize_svg
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
        self.digraph.render(filename, view=True, format="pdf")

    def render_svg(self) -> str:
        return optimize_svg(self.digraph.pipe(format="svg").decode())

    def ipython_display_object(self) -> DisplayObject:
        svg_text = self.render_svg()
        # We emit this HTML to get a zoomable SVG
        # Copied from https://github.com/jupyterlab/jupyterlab/issues/7497#issuecomment-557334236
        # Which references https://github.com/pygraphkit/graphtik/blob/56a513c665e26e7bf3e81b6fb07d9475c5bf1614/graphtik/plot.py#L144-L183
        # Which uses this library: https://github.com/bumbu/svg-pan-zoom
        html_text = f"""
            <div class="svg_container">
                <style>
                    .svg_container SVG {{
                        width: 100%;
                        height: 100%;
                    }}
                </style>
                <script src="https://bumbu.me/svg-pan-zoom/dist/svg-pan-zoom.min.js"></script>
                <script type="text/javascript">
                    var scriptTag = document.scripts[document.scripts.length - 1];
                    var parentTag = scriptTag.parentNode;
                    var svg_el = parentTag.querySelector(".svg_container svg");
                    svgPanZoom(svg_el, {{
                        controlIconsEnabled: true,
                        fit: true,
                        zoomScaleSensitivity: 0.2,
                        minZoom: 0.1,
                        maxZoom: 10
                    }});
                </script>
                {svg_text}
            </div>
        """
        return HTML(html_text)

    @classmethod
    def for_test_snapshot(cls, tracer: Tracer) -> Visualizer:
        """
        Create a graph for saving as a snapshot, to help with visual diffs in PRs.
        """
        options = VisualGraphOptions(
            tracer.graph,
            tracer,
            highlight_node=None,
            # This is genenerally repetitive, and we can avoid it.
            show_implied_mutations=False,
            # Views are too verbose to show in the test output
            show_views=False,
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
            show_artifacts=True,
            show_variables=True,
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
            show_artifacts=False,
            show_variables=False,
        )

        return cls(options)
