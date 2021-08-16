from lineapy.execution.executor import Executor
from tests.stub_data.graph_with_import import graph_with_import
from tests.stub_data.graph_with_pandas import (
    graph_with_pandas,
    session as graph_with_pandas_session,
)
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


class TestBasicExecutor:
    # we should probably do a shared setup in the future
    def test_simple_graph(self):
        # initialize the executor
        e = Executor()
        e.walk(simple_graph)
        a = e.get_value_by_variable_name("a")
        assert a == 11

    def test_nested_call_graph(self):
        e = Executor()
        e.walk(nested_call_graph)
        a = e.get_value_by_variable_name("a")
        assert a == 10

    def test_graph_with_print(self):
        e = Executor()
        e.walk(simple_with_variable_argument_and_print)
        stdout = e.get_stdout()
        assert stdout == "10\n"
        pass

    def test_basic_import(self):
        """
        some imports are built in, such as "math" or "datetime"
        """
        e = Executor()
        e.walk(graph_with_import)
        b = e.get_value_by_variable_name("b")
        assert b == 5

    def test_pip_install_import(self):
        """
        other libs, like pandas, or sckitlearn, need to be pip installed.
        """
        e = Executor()
        e.setup(graph_with_pandas_session)
        e.walk(graph_with_pandas)
        df = e.get_value_by_variable_name("df")
        assert df is not None

    def test_graph_with_function_definition(self):
        """ """
        e = Executor()
        e.walk(graph_with_function_definition)
        a = e.get_value_by_variable_name("a")
        assert a == 120
        pass

    def test_program_with_mutations(self):
        """
        WAIT: need types to be more stable for representing mutation
        """
        pass

    def test_program_with_loops(self):
        e = Executor()
        e.walk(graph_with_loops)
        y = e.get_value_by_variable_name("y")
        x = e.get_value_by_variable_name("x")
        a = e.get_value_by_variable_name("a")
        assert y == 72
        assert x == 36
        assert len(a) == 9

    def test_program_with_conditionals(self):
        e = Executor
        e.walk(graph_with_conditionals)
        bs = e.get_value_by_varable_name("bs")
        # @dhruv TODO assert that bs is the same as [1,2,3]


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
