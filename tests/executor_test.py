import unittest

from lineapy.execution.executor import Executor
from tests.stub_data.graph_with_import import graph_with_import
from tests.stub_data.graph_with_pandas import graph_with_pandas
from tests.stub_data.nested_call_graph import nested_call_graph
from tests.stub_data.simple_graph import simple_graph
from tests.stub_data.simple_with_variable_argument_and_print import (
    simple_with_variable_argument_and_print,
)


class TestBasicExecutor(unittest.TestCase):
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
        e.walk(graph_with_pandas)
        df = e.get_value_by_variable_name("df")
        assert df is not None

    def test_program_with_mutations(self):
        """
        WAIT: need types to be more stable for representing mutation
        """
        pass

    def test_program_with_loops(self):
        pass

    def test_program_with_conditionals(self):
        pass


if __name__ == "__main__":
    tester = TestBasicExecutor()
    tester.simple_graph()
    tester.nested_call_graph()
    tester.graph_with_print()
    tester.basic_import()
    tester.pip_install_import()
