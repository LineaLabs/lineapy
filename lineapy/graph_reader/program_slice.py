import re
from typing import List, Set

from lineapy.data.graph import Graph
from lineapy.data.types import Node, LineaID
from lineapy.graph_reader.graph_util import get_segment_from_code


"""
TODO: for slicing, there are lots of complexities.

- Mutation
    - Examples:
    - Third party libraries have functions that mutate some global or
        variable state.
    - Strategy for now
    - definitely take care of the simple cases, like `VariableNode`
    - simple heuristics that may create false positives
        (include things not necessary)
    - but definitely NOT false negatives (then the program
        CANNOT be executed)
"""


def max_col_of_code(code: str) -> int:
    lines = code.split("\n")
    max_col = 0
    for i in lines:
        if len(i) > max_col:
            max_col = len(i)

    return max_col


def replace_slice_of_code(
    code: str, new_code: str, start: int, end: int
) -> str:
    return code[:start] + new_code + code[end:]


def add_node_to_code(current_code: str, session_code: str, node: Node) -> str:
    """
    FIXME: we should do some type checking on if the lineno etc.
           are defined
    """
    segment = get_segment_from_code(session_code, node)
    segment_lines = segment.split("\n")
    lines = current_code.split("\n")

    # replace empty space
    if node.lineno == node.end_lineno:
        # if it's only a single line to be inserted
        lines[node.lineno - 1] = replace_slice_of_code(
            lines[node.lineno - 1],
            segment,
            node.col_offset,
            node.end_col_offset,
        )
    else:
        # if multiple lines need insertion
        lines[node.lineno - 1] = replace_slice_of_code(
            lines[node.lineno - 1],
            segment_lines[0],
            node.col_offset,
            len(lines[node.lineno - 1]),
        )

        lines[node.end_lineno - 1] = replace_slice_of_code(
            lines[node.end_lineno - 1],
            segment_lines[-1],
            0,
            node.end_col_offset,
        )

        for i in range(1, len(segment_lines) - 1):
            lines[node.lineno - 1 + i] = segment_lines[i]

    return "\n".join(lines)


def get_slice_graph(graph: Graph, sinks: List[LineaID]) -> Graph:
    """
    Takes a full graph from the session
        and produces the subset responsible for the "sinks".

    """
    ancestors: Set[LineaID] = set(sinks)

    for sink in sinks:
        ancestors.update(graph.get_ancestors(sink))
    ancestors.update(sinks)
    new_nodes = [graph.get_node_else_raise(node) for node in ancestors]
    subgraph = graph.get_subgraph(new_nodes)
    return subgraph


def get_source_code_from_graph(program: Graph) -> str:
    session_code = program.source_code

    nodes = [
        node
        for node in program.nodes
        if node.lineno is not None and node.col_offset is not None
    ]

    num_lines = len(session_code.split("\n"))
    code = "\n".join([" " * max_col_of_code(session_code)] * num_lines)

    for node in nodes:
        code = add_node_to_code(code, session_code, node)

    code = re.sub(r"\n\s*\n", "\n\n", code)

    # remove extra white spaces from end of each line
    lines = code.split("\n")
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    code = "\n".join(lines)

    return code


def get_program_slice(graph: Graph, sinks: List[LineaID]) -> str:
    """
    Find the necessary and sufficient code for computing the sink nodes.

    :param program: the computation graph.
    :param sinks: artifacts to get the code slice for.
    :return: string containing the necessary and sufficient code for
    computing sinks.
    """
    subgraph = get_slice_graph(graph, sinks)
    return get_source_code_from_graph(subgraph)
