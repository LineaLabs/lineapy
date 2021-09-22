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
    simple_function_definition_graph,
    session as simple_function_definition_graph_session,
)

from tests.stub_data.graph_with_function_definition import (
    graph_with_function_definition,
    session as graph_with_function_definition_session,
)
from tests.stub_data.graph_with_import import (
    graph_with_import,
    session as graph_with_import_session,
)
from tests.stub_data.graph_with_loops import (
    graph_with_loops,
    session as graph_with_loops_session,
)
from tests.stub_data.nested_call_graph import (
    nested_call_graph,
    session as nested_call_graph_session,
)
from tests.stub_data.simple_graph import (
    simple_graph,
    session as simple_graph_session,
)
from tests.stub_data.simple_with_variable_argument_and_print import (
    simple_with_variable_argument_and_print,
    session as simple_with_variable_argument_and_print_session,
)

from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    session as graph_with_messy_nodes_session,
)


class TestBasicExecutor:
    # we should probably do a shared setup in the future
    def test_simple_graph(self):
        # initialize the executor
        e = Executor()
        e.execute_program(simple_graph)
        a = e.get_value_by_variable_name("a")
        assert a == 11

    def test_nested_call_graph(self):
        e = Executor()
        e.execute_program(nested_call_graph)
        a = e.get_value_by_variable_name("a")
        assert a == 10

    def test_graph_with_print(self):
        e = Executor()
        e.execute_program(simple_with_variable_argument_and_print)
        stdout = e.get_stdout()
        assert stdout == "10\n"

    def test_basic_import(self):
        """
        some imports are built in, such as "math" or "datetime"
        """
        e = Executor()
        e.execute_program(graph_with_import)
        b = e.get_value_by_variable_name("b")
        assert b == 5

    def test_simple_function_definition_graph(self):
        e = Executor()
        e.execute_program(
            simple_function_definition_graph,
        )
        c = e.get_value_by_variable_name("c")
        assert c == 1

    def test_graph_with_function_definition(self):
        """ """
        e = Executor()
        e.execute_program(
            graph_with_function_definition,
        )
        a = e.get_value_by_variable_name("a")
        assert a == 120

    def test_program_with_mutations(self):
        """
        WAIT: need types to be more stable for representing mutation
        """
        pass

    def test_program_with_loops(self):
        e = Executor()
        e.execute_program(graph_with_loops)
        y = e.get_value_by_variable_name("y")
        x = e.get_value_by_variable_name("x")
        a = e.get_value_by_variable_name("a")
        assert y == 72
        assert x == 36
        assert len(a) == 9

    def test_program_with_conditionals(self):
        e = Executor()
        e.execute_program(
            graph_with_conditionals,
        )
        bs = e.get_value_by_variable_name("bs")
        stdout = e.get_stdout()
        assert bs == [1, 2, 3]
        assert stdout == "False\n"

    def test_program_with_file_access(self):
        e = Executor()
        e.execute_program(
            graph_with_csv_import,
        )
        s = e.get_value_by_variable_name("s")
        assert s == 25

    def test_variable_alias_by_value(self):
        e = Executor()
        e.execute_program(graph_with_alias_by_value)
        a = e.get_value_by_variable_name("a")
        b = e.get_value_by_variable_name("b")
        assert a == 2
        assert b == 0

    def test_variable_alias_by_reference(self):
        e = Executor()
        e.execute_program(
            graph_with_alias_by_reference,
        )
        s = e.get_value_by_variable_name("s")
        assert s == 10

    def test_headless_variable_and_literals(self):
        e = Executor()
        e.execute_program(
            graph_with_messy_nodes,
        )
        g = e.get_value_by_variable_name("g")
        assert g == 5

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
