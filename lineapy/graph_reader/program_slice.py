import logging
from typing import DefaultDict, List, Set

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, SourceCode
from lineapy.db.db import RelationalLineaDB

logger = logging.getLogger(__name__)


def get_slice_graph(graph: Graph, sinks: List[LineaID]) -> Graph:
    """
    Takes a full graph from the session
    and produces the subset responsible for the "sinks".

    """
    ancestors: Set[LineaID] = set(sinks)

    for sink in sinks:
        ancestors.update(graph.get_ancestors(sink))

    new_nodes = [graph.ids[node] for node in ancestors]
    subgraph = graph.get_subgraph(new_nodes)
    return subgraph


def get_source_code_from_graph(program: Graph) -> str:
    """
    Returns the code from some subgraph, by including all lines that
    are included in the graphs source.

    TODO: We need better analysis than just looking at the source code.
    For example, what if we just need one expression from a line that defines
    multuple expressions?

    We should probably instead regenerate the source from our graph
    representation.
    """
    # map of source code to set of included line numbers
    source_code_to_lines = DefaultDict[SourceCode, Set[int]](set)

    for node in program.nodes:
        if not node.source_location:
            continue
        source_code_to_lines[node.source_location.source_code] |= set(
            range(
                node.source_location.lineno,
                node.source_location.end_lineno + 1,
            )
        )

    logger.debug("Source code to lines: %s", source_code_to_lines)
    # Sort source codes (for jupyter cells), and select lines
    code = ""
    for source_code, lines in sorted(
        source_code_to_lines.items(), key=lambda x: x[0]
    ):
        source_code_lines = source_code.code.split("\n")
        for line in sorted(lines):
            code += source_code_lines[line - 1] + "\n"

    return code


def get_program_slice(graph: Graph, sinks: List[LineaID]) -> str:
    """
    Find the necessary and sufficient code for computing the sink nodes.

    :param program: the computation graph.
    :param sinks: artifacts to get the code slice for.
    :return: string containing the necessary and sufficient code for
             computing sinks.

    """
    logger.debug("Slicing graph %s", graph)
    subgraph = get_slice_graph(graph, sinks)
    logger.debug("Subgraph for %s: %s", sinks, subgraph)
    return get_source_code_from_graph(subgraph)


def get_program_slice_by_artifact_name(
    db: RelationalLineaDB, name: str
) -> str:
    artifact = db.get_artifact_by_name(name)
    nodes = db.get_nodes_for_session(artifact.node.session_id)
    graph = Graph(nodes, db.get_session_context(artifact.node.session_id))
    return get_program_slice(graph, [artifact.node_id])
