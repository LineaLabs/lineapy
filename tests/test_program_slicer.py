from lineapy.graph_reader.program_slice import get_program_slice
from tests.stub_data.graph_with_function_definition import (
    graph_with_function_definition,
    my_function_call,
    code as function_code,
)

from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    f_assign,
    sliced_code as sliced_messy_graph,
)

from tests.stub_data.graph_with_simple_slicing import (
    graph_with_simple_slicing,
    c_assign,
    sliced_code,
)

from tests.util import compare_code_via_ast


class TestProgramSlicer:
    """
    TODO: in the future we should add more cases for
    - globals
    - mutations
    """

    def test_simple_assignment(self):
        code_slice = get_program_slice(graph_with_simple_slicing, [c_assign.id])
        assert compare_code_via_ast(code_slice, sliced_code)

    def test_messy_graph(self):
        code_slice = get_program_slice(graph_with_messy_nodes, [f_assign.id])
        assert compare_code_via_ast(code_slice, sliced_messy_graph)

    def test_calls(self):
        # Check to make sure it does not drop global references
        code_slice = get_program_slice(
            graph_with_function_definition, [my_function_call.id]
        )
        assert compare_code_via_ast(code_slice, function_code)
