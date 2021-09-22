import pytest

from lineapy.execution.executor import Executor
from tests.stub_data.graph_with_alias_by_reference import (
    graph_with_alias_by_reference,
    session as graph_with_alias_by_reference_session,
)
from tests.stub_data.graph_with_alias_by_value import (
    graph_with_alias_by_value,
    session as graph_with_alias_by_value_session,
)
from tests.stub_data.graph_with_conditionals import (
    graph_with_conditionals,
    session as graph_with_conditionals_session,
)
from tests.stub_data.graph_with_csv_import import (
    graph_with_csv_import,
    session as graph_with_file_access_session,
)
from tests.stub_data.graph_with_simple_function_definition import (
    code as simple_function_definition_graph_code,
)

from tests.stub_data.graph_with_function_definition import (
    graph_with_function_definition,
    session as graph_with_function_definition_session,
)
from tests.stub_data.graph_with_import import (
    code as graph_with_import_code,
)
from tests.stub_data.graph_with_loops import (
    graph_with_loops,
    session as graph_with_loops_session,
)
from tests.stub_data.nested_call_graph import (
    code as nested_call_graph_code,
)


from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    session as graph_with_messy_nodes_session,
    code as graph_with_messy_nodes_code,
)


class TestBasicExecutor:
    def test_nested_call_graph(self, execute):
        res = execute(nested_call_graph_code)
        assert res.values["a"] == 10

    def test_basic_import(self, execute):
        """
        some imports are built in, such as "math" or "datetime"
        """
        res = execute(graph_with_import_code)
        assert res.values["b"] == 5

    def test_simple_function_definition_graph(self, execute):
        res = execute(simple_function_definition_graph_code)
        assert res.values["c"] == 1

    # TODO: Move to E2E when function definitions that edit globals work
    def test_graph_with_function_definition(self):
        """ """
        e = Executor()
        e.execute_program(
            graph_with_function_definition,
            graph_with_function_definition_session,
        )
        a = e.get_value_by_variable_name("a")
        assert a == 120

    def test_program_with_mutations(self):
        """
        WAIT: need types to be more stable for representing mutation
        """
        pass

    # TODO: Move to E2E test when loops work
    def test_program_with_loops(self):
        e = Executor()
        e.execute_program(graph_with_loops, graph_with_loops_session)
        y = e.get_value_by_variable_name("y")
        x = e.get_value_by_variable_name("x")
        a = e.get_value_by_variable_name("a")
        assert y == 72
        assert x == 36
        assert len(a) == 9

    # TODO: Remove when https://github.com/LineaLabs/lineapy/issues/180 is fixed
    # and enable as end to end test
    def test_program_with_conditionals(self):
        e = Executor()
        e.execute_program(
            graph_with_conditionals,
            graph_with_conditionals_session,
        )
        bs = e.get_value_by_variable_name("bs")
        stdout = e.get_stdout()
        assert bs == [1, 2, 3]
        assert stdout == "False\n"

    # TODO: Remove when https://github.com/LineaLabs/lineapy/issues/178 is fixed
    # and enable as end to end test
    def test_program_with_file_access(self):
        e = Executor()
        e.execute_program(
            graph_with_csv_import,
            graph_with_file_access_session,
        )
        s = e.get_value_by_variable_name("s")
        assert s == 25

    # TODO: Remove when https://github.com/LineaLabs/lineapy/issues/155 is fixed
    # and enable as end to end test
    def test_variable_alias_by_value(self):
        e = Executor()
        e.execute_program(
            graph_with_alias_by_value, graph_with_alias_by_value_session
        )
        a = e.get_value_by_variable_name("a")
        b = e.get_value_by_variable_name("b")
        assert a == 2
        assert b == 0

    # TODO: Remove when https://github.com/LineaLabs/lineapy/issues/155 is fixed
    # and enable as end to end test
    def test_variable_alias_by_reference(self):
        e = Executor()
        e.execute_program(
            graph_with_alias_by_reference,
            graph_with_alias_by_reference_session,
        )
        s = e.get_value_by_variable_name("s")
        assert s == 10

    # TODO: Remove when https://github.com/LineaLabs/lineapy/issues/155 is fixed
    # and enable as end to end test
    def test_headless_variable_and_literals(self, execute):
        e = Executor()
        e.execute_program(
            graph_with_messy_nodes,
            graph_with_messy_nodes_session,
        )
        g = e.get_value_by_variable_name("g")
        assert g == 5

        res = execute(
            graph_with_messy_nodes_code,
            exec_transformed_xfail="https://github.com/LineaLabs/lineapy/issues/155",
        )
        assert res.values["g"] == 5

    def test_execute_program_with_inputs_graph_with_loops(self):
        # e = Executor()
        # from tests.stub_data.graph_with_loops import a_argument_id
        # e.execute_program_with_inputs(graph_with_loops,
        #  {a_argument_id: [1, 2, 3]})
        # x = e.get_value_by_variable_name('x')
        # assert x == 6
        # y = e.get_value_by_variable_name('y')
        # assert y == 6
        pass

    def test_execute_program_with_inputs_graph_with_conditionals(self):
        # e = Executor()
        # from tests.stub_data.graph_with_conditionals import bs_line_id
        # e.execute_program_with_inputs(graph_with_loops,
        # {bs_line_id: [1, 2, 3, 4, 5]})
        # stdout = e.get_stdout()
        # assert stdout == "True\n"
        pass
