from pathlib import PosixPath
from typing import Optional
from unittest.mock import MagicMock

from lineapy.data.graph import Graph
from lineapy.data.types import (
    LineaID,
    LiteralNode,
    NodeType,
    SourceCode,
    SourceLocation,
)
from lineapy.graph_reader.program_slice import (
    _include_dependencies_for_indirectly_included_nodes_in_slice,
    get_subgraph_nodelist,
)

source_1 = SourceCode(
    id="0",
    code="",
    location=PosixPath("[source file path]"),
)


def get_dummy_node(id: str, line_no: int, dependency: Optional[str]):
    return LiteralNode(
        id=LineaID(id),
        value=None,
        session_id="x",
        node_type=NodeType.Node,
        source_location=SourceLocation(
            lineno=line_no,
            end_lineno=line_no,
            col_offset=0,
            end_col_offset=0,
            source_code=source_1,
        ),
        control_dependency=LineaID(dependency) if dependency else None,
    )


def test_include_dependencies_for_indirectly_included_nodes_in_slice():
    mocked_session = MagicMock()
    # Graph being tested:
    #
    # line 1:   Instruction 1
    # line 2:   Instruction 2; Instruction 3
    #
    # Slice on Instruction 3
    #
    # Instruction 3 depends on Instruction 1, Instruction 2 is independent
    #
    # If _include_dependencies_for_indirectly_included_nodes_in_slice was not
    # present, we would include Instruction 1 and Instruction 3, which means
    # lines 1 and 2 both get included, which indirectly includes Instruction 2,
    # but the get_subgraph_nodelist would not include Instruction 2's node.
    nodes = [
        get_dummy_node("1", 1, None),
        get_dummy_node("2", 2, None),
        get_dummy_node("3", 2, "1"),
    ]
    graph = Graph(list(nodes), mocked_session)
    ancestors = get_subgraph_nodelist(graph, [LineaID("3")], False)
    assert ancestors == {"1", "3"}
    ancestors = _include_dependencies_for_indirectly_included_nodes_in_slice(
        graph, ancestors
    )
    assert ancestors == {"1", "2", "3"}


def test_include_dependencies_for_indirectly_included_nodes_in_slice_recursive():
    mocked_session = MagicMock()
    # Graph being tested:
    #
    # line 1:   Instruction 1
    # line 2:   Instruction 2
    # line 3:   Instruction 3; Instruction 4
    # line 4:   Instruction 5; Instruction 6
    #
    # Slice on Instruction 5
    #
    # Instruction 5 depends on Instruction 1, Instruction 3 depends on
    # Instruction 2, Instruction 6 depends on Instruction 4
    #
    # If _include_dependencies_for_indirectly_included_nodes_in_slice was not
    # present, we would include Instruction 1 and Instruction 5, which means
    # lines 1 and 4 both get included, which indirectly includes Instruction 6,
    # but the get_subgraph_nodelist would not include Instruction 2's node.
    #
    # If _include_dependencies_for_indirectly_included_nodes_in_slice was not
    # recursive, the process would stop after including line 3, but due to
    # Instruction 3 also depending on Instruction 2, we should also include
    # line 2 as well, and the process could continue multiple times.
    nodes = [
        get_dummy_node("1", 1, None),
        get_dummy_node("2", 2, None),
        get_dummy_node("3", 3, "2"),
        get_dummy_node("4", 3, None),
        get_dummy_node("5", 4, "1"),
        get_dummy_node("6", 4, "4"),
    ]
    graph = Graph(list(nodes), mocked_session)
    ancestors = get_subgraph_nodelist(graph, [LineaID("5")], False)
    assert ancestors == {"1", "5"}
    ancestors = _include_dependencies_for_indirectly_included_nodes_in_slice(
        graph, ancestors
    )
    assert ancestors == {"1", "2", "3", "4", "5", "6"}
