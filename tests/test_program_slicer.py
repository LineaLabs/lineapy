from lineapy.graph_reader.program_slice import ProgramSlicer
from tests.stub_data.graph_with_function_definition import (
    graph_with_function_definition,
    my_function_call,
    code as function_code,
)
from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    f_assign,
    sliced_code,
    code,
)

from tests.util import compare_code_via_ast


class TestProgramSlicer:
    def test_simple_assignment(self):
        graph_with_messy_nodes.code = code
        program_slicer = ProgramSlicer()
        code_slice = program_slicer.get_slice(graph_with_messy_nodes, [f_assign])
        assert compare_code_via_ast(code_slice, sliced_code)

    def test_calls(self):
        # Check to make sure it does not drop global references
        graph_with_function_definition.code = function_code
        program_slicer = ProgramSlicer()
        code_slice = program_slicer.get_slice(
            graph_with_function_definition, [my_function_call]
        )
        assert compare_code_via_ast(code_slice, function_code)
