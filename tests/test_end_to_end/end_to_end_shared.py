from tempfile import NamedTemporaryFile
from typing import Any

from lineapy.data.types import SessionType, NodeType
from tests.util import run_code
from lineapy.graph_reader.graph_util import are_nodes_content_equal
from lineapy.cli.cli import linea_cli
from tests.stub_data.simple_graph import simple_graph_code, line_1, arg_literal
from tests.stub_data.graph_with_simple_function_definition import (
    definition_node,
    assignment_node,
    code as function_definition_code,
)


def simple_graph(session_type: SessionType, db: Any):
    tmp_file_name = run_code(
        simple_graph_code,
        "simple graph code",
        session_type,
    )
    nodes = db.get_nodes_by_file_name(tmp_file_name)
    # there should just be two
    assert len(nodes) == 2
    for c in nodes:
        if c.node_type == NodeType.CallNode:
            assert are_nodes_content_equal(
                c, line_1, db.get_context(nodes[0].session_id).code
            )
        if c.node_type == NodeType.ArgumentNode:
            assert are_nodes_content_equal(
                c,
                arg_literal,
                db.get_context(nodes[0].session_id).code,
            )


def simple_function_def(session_type: SessionType, db: Any, runner: Any):
    with NamedTemporaryFile() as tmp:
        tmp.write(str.encode(function_definition_code))
        tmp.flush()
        # might also need os.path.dirname() in addition to file name
        tmp_file_name = tmp.name
        # FIXME: make into constants
        result = runner.invoke(
            linea_cli,
            ["--mode", "dev", tmp_file_name],
        )
        assert result.exit_code == 0
        nodes = db.get_nodes_by_file_name(tmp_file_name)
        assert len(nodes) == 2
        for c in nodes:
            if c.node_type == NodeType.FunctionDefinitionNode:
                assert are_nodes_content_equal(
                    c,
                    definition_node,
                    function_definition_code,
                )
            if c.node_type == NodeType.CallNode:
                assert are_nodes_content_equal(
                    c,
                    assignment_node,
                    function_definition_code,
                )
