import logging
from collections import defaultdict
from typing import List, Set

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, SourceCode

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
    source_code_to_lines = defaultdict[SourceCode, set[int]](set)

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


def split_code_blocks(code: str, func_name: str):
    """
    Split the list of code lines to import, main code and main func blocks.
    The code block is added under a function with given name.

    :param code: the source code to split.
    :param func_name: name of the function to create.
    :return: strings representing import_block, code_block, main_block.
    """
    # We split the lines in import and code blocks and join them to full code test
    lines = code.split("\n")
    # Impotrs are at the top, find where they end
    end_of_imports_line_num = 0
    import_open_braket = False
    while (
        "import" in lines[end_of_imports_line_num]
        or "#" in lines[end_of_imports_line_num]
        or "" == lines[end_of_imports_line_num]
        or "    " in lines[end_of_imports_line_num]
        and import_open_braket
        or ")" in lines[end_of_imports_line_num]
        and import_open_braket
    ):
        if "(" in lines[end_of_imports_line_num]:
            import_open_braket = True
        elif ")" in lines[end_of_imports_line_num]:
            import_open_braket = False
        end_of_imports_line_num += 1
    # everything from here down needs to be under def()
    # TODO Support arguments to the func
    code_block = f"def {func_name}():\n\t" + "\n\t".join(
        lines[end_of_imports_line_num:]
    )
    import_block = "\n".join(lines[:end_of_imports_line_num])
    main_block = f"""if __name__ == "__main__":\n\tprint({func_name}())"""
    return import_block, code_block, main_block
