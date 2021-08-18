from lineapy.execution.executor import Executor
from tests.stub_data.graph_with_import import graph_with_import
from tests.stub_data.nested_call_graph import nested_call_graph
from tests.stub_data.simple_graph import simple_graph
from tests.stub_data.graph_with_loops import graph_with_loops
from tests.stub_data.graph_with_conditionals import graph_with_conditionals
from tests.stub_data.graph_with_function_definition import (
    graph_with_function_definition,
)
from tests.stub_data.simple_with_variable_argument_and_print import (
    simple_with_variable_argument_and_print,
)

from tests.stub_data.graph_with_csv_import import (
    graph_with_csv_import,
    session as graph_with_file_access_session,
)

from tests.stub_data.graph_with_variable_alias import (
    graph_with_alias_by_reference,
    graph_with_alias_by_value,
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

    def test_graph_with_function_definition(self):
        """ """
        e = Executor()
        e.execute_program(graph_with_function_definition)
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
        e.execute_program(graph_with_conditionals)
        bs = e.get_value_by_variable_name("bs")
        stdout = e.get_stdout()
        assert bs == [1, 2, 3]
        assert stdout == "False\n"

    def test_program_with_file_access(self):
        e = Executor()
        e.setup(graph_with_file_access_session)
        e.execute_program(graph_with_csv_import)
        s = e.get_value_by_variable_name("s")
        assert s == 25

    def test_variable_alias_by_value(self):
        e = Executor()
        e.execute_program(graph_with_literal_alias)
        a = e.get_value_by_variable_name("a")
        b = e.get_value_by_variable_name("b")
        assert a == 2
        assert b == 0

    def test_variable_alias_by_reference(self):
        e = Executor()
        e.execute_program(graph_with_literal_alias)
        s = e.get_value_by_variable_name("2")
        assert s == 10
        assert b == 0


if __name__ == "__main__":
    tester = TestBasicExecutor()
    tester.test_simple_graph()
    tester.test_nested_call_graph()
    tester.test_graph_with_print()
    tester.test_basic_import()
    tester.test_pip_install_import()
    tester.test_graph_with_function_definition()
    tester.test_program_with_mutations()
    tester.test_program_with_loops()
    tester.test_program_with_conditionals()
