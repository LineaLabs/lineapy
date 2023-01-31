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

    Parameters
    ----------
    graph: Graph
        A full graph objection from a session.
    sinks: List[LineaID]
        A list of node IDs desired for slicing.
    keep_lineapy_save: bool
        Whether to retain ``lineapy.save()`` in code slice.

    Returns
    -------
    Graph
        A subgraph extracted (i.e., sliced) for the desired node IDs.

    """
    ancestors = get_subgraph_nodelist(graph, sinks, keep_lineapy_save)

    ancestors = _include_dependencies_for_indirectly_included_nodes_in_slice(
        graph, ancestors
    )

    new_nodes = [graph.ids[node] for node in ancestors]
    subgraph = graph.get_subgraph(new_nodes)
    return subgraph


def get_subgraph_nodelist(
    graph: Graph, sinks: List[LineaID], keep_lineapy_save: bool
) -> Set[LineaID]:
    """
    Computes a preliminary slice first evaluates what all nodes serve as sinks,
    and then for each of the sinks from what all nodes in the graph, can the
    sinks be reached (all ancestors of all sinks)
    Note that this function is not the final slice as it is possible that some
    relevant nodes are not included through the ancestor relation. For more
    details see  _include_dependencies_for_indirectly_included_nodes_in_slice
    """
    for node in graph.nodes:
        # If there is a control flow node which has a branch which was never
        # encountered during runtime, we take a conservative approach and
        # include all of the lines present in the unexecuted code block so that
        # in case the branch is visited during production, we do not alter the
        # user's intended behavior
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

    return ancestors


def _include_dependencies_for_indirectly_included_nodes_in_slice(
    graph: Graph, current_subset: Set[LineaID]
) -> Set[LineaID]:
    """
    Ensures that for each line in the sliced program output, all corresponding
    nodes are included in the selected subgraph, and vice versa
    """
    # TODO: Change the recursive function into a iterative/one-pass solution
    # for speed.
    #
    # LineaPy's graph slicing mechanism takes in the Linea Graph, obtains a
    # subset of the nodes which are necessary for the required artifact, and
    # then selects the line numbers which the selected nodes of the subgraph
    # correspond to. However, it is possible that there may be lines with
    # multiple statements as follows:
    #
    #   a = []
    #   b = []
    #   a.append(10);b.append(20)
    #   lineapy.save(a, 'a')
    #
    # In this case, our slicer would identify that lines 1, 3 and 4 are
    # relevant for the artifact, and the slice generated would be as follows:
    #
    #   a = []
    #   a.append(10);b.append(20)
    #
    # This code would not compile as `b.append(20)` relies on `b` being
    # declared before, and hence our generated code would crash. To avoid this
    # scenario, this function takes in the selected subgraph, finds out all
    # relevant line numbers to be included, and checks whether there are any
    # additional nodes whose line numbers intersect with already included line
    # numbers, and adds those nodes and their ancestors to the graph. This
    # process may increase the set of included line numbers, hence this
    # function is called recursively.
    code_to_lines = DefaultDict[SourceCode, Set[int]](set)

    for node_id in current_subset:
        node = graph.get_node(node_id)
        if node is None or not node.source_location:
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
            if (
                node is None
                or isinstance(node, ImportNode)
                or not node.source_location
            ):
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
        return _include_dependencies_for_indirectly_included_nodes_in_slice(
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


def get_source_code_from_graph(
    slice_nodes: Set[LineaID],
    session_graph: Graph,
    include_non_slice_as_comment=False,
) -> CodeSlice:
    """
    Returns the code from some subgraph, by including all lines that
    are included in the graphs source.
    """
    # TODO: We need better analysis than just looking at the source code.
    # For example, what if we just need one expression from a line that defines
    # multiple expressions? We should probably instead regenerate the source from
    # our graph representation.

    # map of source code to set of included line numbers
    source_code_to_lines = DefaultDict[SourceCode, Set[int]](set)
    import_code_to_lines = DefaultDict[SourceCode, Set[int]](set)
    incomplete_block_locations = DefaultDict[SourceCode, Set[int]](set)
    session_src = DefaultDict[SourceCode, Set[LineaID]](set)

    for nodeid in slice_nodes:
        node = session_graph.ids[nodeid]
        if not node.source_location:
            continue
        # In the following code sample:
        #
        # a = [10]
        # if a.pop() > 5:
        #       print(a)
        # lineapy.save(a, 'a')
        #
        # If we slice on `a``, we note that all of the statements inside the if
        # block get sliced out. Technically, one could say that the slice is:
        #
        # a = [10]
        # if a.pop() > 5:
        #
        # Since the test condition of the if block modifies `a`, hence it must
        # be included, and since print() statements do not affect `a`, we can
        # slice them out. However, the generated code is not syntactically
        # valid Python code, and hence we need to add a `pass` statement to
        # ensure it compiles like the following:
        #
        # a = [10]
        # if a.pop() > 5:
        #       pass
        #
        # To find out the program locations where we need to append a `pass`
        # statement, we maintain the `incomplete_block_location` variable to
        # keep a track of these program lines.

        if isinstance(node, (ControlFlowNode)):
            control_dependencies = [
                child_id
                for child_id in session_graph.get_children(nodeid)
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

    for n in session_graph.nodes:
        if n.source_location is None:
            continue
        # ignore the code cells that have no part in the slice at all
        if (
            not include_non_slice_as_comment
            and n.source_location.source_code not in source_code_to_lines
        ):
            continue
        session_src[n.source_location.source_code] |= set([n.id])

    logger.debug("Source code to lines: %s", source_code_to_lines)
    # Sort source codes (for jupyter cells), and select lines
    body_code = []
    for source_code, nodeids in sorted(
        session_src.items(), key=lambda x: x[0]
    ):
        # if any of the nodeids in a sourcecode block are in source_code_to_lines,
        # then there are pieces of the codecell in the final slice.
        lines = source_code_to_lines.get(source_code, set())
        source_code_lines = source_code.code.split("\n")
        if not include_non_slice_as_comment:
            for line in sorted(lines):
                body_code.append(source_code_lines[line - 1])
                if line in incomplete_block_locations[source_code]:
                    line_str = source_code_lines[line - 1]
                    indent = len(line_str) - len(line_str.lstrip())
                    body_code.append(" " * (indent + 1) + "pass")
        else:

            # add the lines that are not part of slice as comments
            for i in range(len(source_code_lines)):
                # lineno is 1-indexed in ast
                if i + 1 in lines:
                    # this is part of slice
                    body_code.append(source_code_lines[i])
                else:
                    # this is not part of slice and should be commented out.
                    body_code.append("# " + source_code_lines[i])

    import_code = []
    for import_source_code, lines in sorted(
        import_code_to_lines.items(), key=lambda x: x[0]
    ):
        import_code_lines = import_source_code.code.split("\n")
        if not include_non_slice_as_comment:
            for line in sorted(lines):
                import_code.append(import_code_lines[line - 1])
        else:
            # add the lines that are not part of slice as comments
            for i in range(len(import_code_lines)):
                # lineno is 1-indexed in ast
                if i + 1 in lines:
                    # this is part of slice
                    import_code.append(import_code_lines[i])
                else:
                    # this is not part of slice and should be commented out.
                    import_code.append("# " + import_code_lines[i])

    return CodeSlice(import_code, body_code)


def get_program_slice(
    graph: Graph, sinks: List[LineaID], keep_lineapy_save: bool = False
) -> CodeSlice:
    """
    Find the necessary and sufficient code for computing the sink nodes.

    Parameters
    ----------
    graph: Graph
        The computation graph.
    sinks: List[LineaID]
        Artifacts to get the code slice for.
    keep_lineapy_save: bool
        Whether to retain ``lineapy.save()`` in code slice.

    Returns
    -------
    CodeSlice
        String containing the necessary and sufficient code for computing sinks

    """
    logger.debug("Slicing graph %s", graph)
    subgraph_nodes = get_subgraph_nodelist(graph, sinks, keep_lineapy_save)
    subgraph_nodes = (
        _include_dependencies_for_indirectly_included_nodes_in_slice(
            graph, subgraph_nodes
        )
    )
    return get_source_code_from_graph(subgraph_nodes, graph)


def get_program_slice_by_artifact_name(
    db: RelationalLineaDB, name: str, keep_lineapy_save: bool = False
) -> CodeSlice:
    artifact = db.get_artifactorm_by_name(name)
    nodes = db.get_nodes_for_session(artifact.node.session_id)
    graph = Graph(nodes, db.get_session_context(artifact.node.session_id))
    return get_program_slice(graph, [artifact.node_id], keep_lineapy_save)
