import re
from typing import List, Set, Optional

from lineapy import Graph
from lineapy.data.types import Node, LineaID
from lineapy.graph_reader.base import GraphReader
from lineapy.graph_reader.graph_util import get_segment_from_code


class ProgramSlicer(GraphReader):
    """ """

    @staticmethod
    def max_col_of_code(code: str) -> int:
        lines = code.split("\n")
        max_col = 0
        for i in lines:
            if len(i) > max_col:
                max_col = len(i)

        return max_col

    @staticmethod
    def replace_slice_of_code(
        code: str, new_code: str, start: int, end: int
    ) -> str:
        return code[:start] + new_code + code[end:]

    @staticmethod
    def add_node_to_code(
        current_code: str, session_code: str, node: Node
    ) -> str:
        segment = get_segment_from_code(session_code, node)
        segment_lines = segment.split("\n")
        lines = current_code.split("\n")

        # replace empty space
        if node.lineno == node.end_lineno:
            # if it's only a single line to be inserted
            lines[node.lineno - 1] = ProgramSlicer.replace_slice_of_code(
                lines[node.lineno - 1],
                segment,
                node.col_offset,
                node.end_col_offset,
            )
        else:
            # if multiple lines need insertion
            lines[node.lineno - 1] = ProgramSlicer.replace_slice_of_code(
                lines[node.lineno - 1],
                segment_lines[0],
                node.col_offset,
                len(lines[node.lineno - 1]),
            )

            lines[node.end_lineno - 1] = ProgramSlicer.replace_slice_of_code(
                lines[node.end_lineno - 1],
                segment_lines[-1],
                0,
                node.end_col_offset,
            )

            for i in range(1, len(segment_lines) - 1):
                lines[node.lineno - 1 + i] = segment_lines[i]

        return "\n".join(lines)

    def validate(self, graph: Graph) -> None:
        pass

    def get_slice(
        self, program: Graph, sinks: Optional[List[Node]] = None
    ) -> str:
        """
        Find the necessary and sufficient code for computing the sink nodes.
        If sinks are None, use the leaf nodes in the program Graph as sinks.

        :param program: the computation graph.
        :param sinks: artifacts to get the code slice for.
        :return: string containing the necessary and sufficient code for
        computing sinks.
        """
        if sinks is None:
            sinks = [
                program.get_node(node) for node in program.get_leaf_nodes()
            ]
        ancestors: Set[LineaID] = set([node.id for node in sinks])

        for sink in sinks:
            ancestors.update(program.get_ancestors(sink))
        subgraph = Graph([program.get_node(node) for node in ancestors])
        subgraph.code = program.code
        return self.walk(subgraph)

    def walk(self, program: Graph) -> str:
        session_code = program.code

        nodes = [
            node
            for node in program.nodes
            if node.lineno is not None and node.col_offset is not None
        ]

        num_lines = len(session_code.split("\n"))
        code = "\n".join(
            [" " * ProgramSlicer.max_col_of_code(session_code)] * num_lines
        )

        for node in nodes:
            code = ProgramSlicer.add_node_to_code(code, session_code, node)

        code = re.sub(r"\n\s*\n", "\n\n", code)

        # remove extra white spaces from end of each line
        lines = code.split("\n")
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip()
        code = "\n".join(lines)

        return code
