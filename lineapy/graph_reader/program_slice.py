import logging
from dataclasses import dataclass
from typing import DefaultDict, List, Set

from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    ControlFlowNode,
    ImportNode,
    LineaID,
    SourceCode,
)
from lineapy.db.db import RelationalLineaDB
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)


def get_slice_graph(
    graph: Graph, sinks: List[LineaID], keep_lineapy_save: bool = False
) -> Graph:
    """
    Takes a full graph from the session
    and produces the subset responsible for the "sinks".

    :param graph: A full graph objection from a session.
    :param sinks: A list of node IDs desired for slicing.
    :param keep_lineapy_save: Whether to retain ``lineapy.save()`` in code slice.
            Defaults to ``False``.
    :return: A subgraph extracted (i.e., sliced) for the desired node IDs.

    """
    for node in graph.nodes:
        if isinstance(node, ControlFlowNode):
            if node.unexec_id is not None:
                sinks.append(node.id)

    if keep_lineapy_save:
        # Children of an artifact sink include .save() statement.
        # Identify .save() statement and make it the new sink.
        # If not applicable, retain the original artifact sink.
        new_sinks = []
        for sink in sinks:
            new_sink = sink
            child_ids = graph.get_children(sink)
            for c_id in child_ids:
                c_node = graph.get_node(c_id)
                if isinstance(c_node, CallNode) and c_node.source_location:
                    source_code = c_node.source_location.source_code.code
                    line_number = c_node.source_location.lineno
                    line_code = source_code.split("\n")[line_number - 1]
                    first_arg = c_node.positional_args[0]
                    if "lineapy.save" in line_code and first_arg.id == sink:
                        new_sink = c_id
            new_sinks.append(new_sink)
        sinks = new_sinks

    ancestors: Set[LineaID] = set(sinks)

    for sink in sinks:
        ancestors.update(graph.get_ancestors(sink))

    ancestors = include_dependencies_for_indirectly_included_nodes_in_slice(
        graph, ancestors
    )

    new_nodes = [graph.ids[node] for node in ancestors]
    subgraph = graph.get_subgraph(new_nodes)
    return subgraph


def include_dependencies_for_indirectly_included_nodes_in_slice(
    graph: Graph, current_subset: Set[LineaID]
) -> Set[LineaID]:
    code_to_lines = DefaultDict[SourceCode, Set[int]](set)

    for node_id in current_subset:
        node = graph.get_node(node_id)
        if node is None:
            continue
        if not node.source_location:
            continue
        code_to_lines[node.source_location.source_code] |= set(
            range(
                node.source_location.lineno,
                node.source_location.end_lineno + 1,
            )
        )

    to_be_added = set()
    completed = True

    for node in graph.nodes:
        node_id = node.id  # type: ignore
        if node_id not in current_subset:
            node = graph.get_node(node_id)
            if isinstance(node, ImportNode):
                continue
            if node is None:
                continue
            if not node.source_location:
                continue
            if (
                set(
                    range(
                        node.source_location.lineno,
                        node.source_location.end_lineno + 1,
                    )
                )
                & code_to_lines[node.source_location.source_code]
            ):
                to_be_added |= {node_id}
                completed = False

    for node_id in to_be_added:
        current_subset |= {node_id}
        current_subset.update(graph.get_ancestors(node_id))

    if completed:
        return current_subset
    else:
        return include_dependencies_for_indirectly_included_nodes_in_slice(
            graph, current_subset
        )


@dataclass
class CodeSlice:
    import_lines: List[str]
    body_lines: List[str]
    # source_code: SourceCode

    def __str__(self):
        return prettify("\n".join(self.import_lines + self.body_lines) + "\n")

    def __repr__(self):
        return str(self)


def get_source_code_from_graph(program: Graph) -> CodeSlice:
    """
    Returns the code from some subgraph, by including all lines that
    are included in the graphs source.

    .. todo:: We need better analysis than just looking at the source code.
        For example, what if we just need one expression from a line that defines
        multiple expressions?

        We should probably instead regenerate the source from our graph
        representation.


    """
    # map of source code to set of included line numbers
    source_code_to_lines = DefaultDict[SourceCode, Set[int]](set)
    import_code_to_lines = DefaultDict[SourceCode, Set[int]](set)
    incomplete_block_locations = DefaultDict[SourceCode, Set[int]](set)

    for node in program.nodes:
        if not node.source_location:
            continue
        if isinstance(node, (ControlFlowNode)):
            control_dependencies = [
                child_id
                for child_id in program.get_children(node.id)
                if not child_id == node.companion_id
            ] + ([node.unexec_id] if node.unexec_id is not None else [])
            if len(control_dependencies) == 0:
                incomplete_block_locations[
                    node.source_location.source_code
                ] |= {node.source_location.end_lineno}
        # check if import node
        if isinstance(node, (ImportNode)):
            import_code_to_lines[node.source_location.source_code] |= set(
                range(
                    node.source_location.lineno,
                    node.source_location.end_lineno + 1,
                )
            )
        else:
            source_code_to_lines[node.source_location.source_code] |= set(
                range(
                    node.source_location.lineno,
                    node.source_location.end_lineno + 1,
                )
            )

    logger.debug("Source code to lines: %s", source_code_to_lines)
    # Sort source codes (for jupyter cells), and select lines
    body_code = []
    for source_code, lines in sorted(
        source_code_to_lines.items(), key=lambda x: x[0]
    ):
        source_code_lines = source_code.code.split("\n")
        for line in sorted(lines):
            body_code.append(source_code_lines[line - 1])
            if line in incomplete_block_locations[source_code]:
                line_str = source_code_lines[line - 1]
                indent = len(line_str) - len(line_str.lstrip())
                body_code.append(" " * (indent + 1) + "pass")

    import_code = []
    for import_source_code, lines in sorted(
        import_code_to_lines.items(), key=lambda x: x[0]
    ):
        import_code_lines = import_source_code.code.split("\n")
        for line in sorted(lines):
            import_code.append(import_code_lines[line - 1])

    return CodeSlice(import_code, body_code)


def get_program_slice(
    graph: Graph, sinks: List[LineaID], keep_lineapy_save: bool = False
) -> CodeSlice:
    """
    Find the necessary and sufficient code for computing the sink nodes.

    :param graph: The computation graph.
    :param sinks: Artifacts to get the code slice for.
    :param keep_lineapy_save: Whether to retain ``lineapy.save()`` in code slice.
            Defaults to ``False``.
    :return: String containing the necessary and sufficient code for
            computing sinks.

    """
    logger.debug("Slicing graph %s", graph)
    subgraph = get_slice_graph(graph, sinks, keep_lineapy_save)
    logger.debug("Subgraph for %s: %s", sinks, subgraph)
    return get_source_code_from_graph(subgraph)


def get_program_slice_by_artifact_name(
    db: RelationalLineaDB, name: str, keep_lineapy_save: bool = False
) -> CodeSlice:
    artifact = db.get_artifact_by_name(name)
    nodes = db.get_nodes_for_session(artifact.node.session_id)
    graph = Graph(nodes, db.get_session_context(artifact.node.session_id))
    return get_program_slice(graph, [artifact.node_id], keep_lineapy_save)
