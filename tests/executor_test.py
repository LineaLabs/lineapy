from lineapy.execution.executor import Executor
import unittest

from tests.stub_data.simple_graph import simple_graph
from tests.stub_data.print_graph import print_graph


class TestBasicExecutor(unittest.TestCase):
    # we should probably do a shared setup in the future
    def simple_graph(self):
        # initialize the executor
        e = Executor()
        e.walk(simple_graph)
        a = e.get_value_by_varable_name("a")
        assert a == 1
        # this should

    def graph_with_print(self):
        e = Executor()
        e.walk(print_graph)
        stdout = e.get_stdout()
        assert stdout == "1"

    def basic_import(self):
        """
        some imports are built in, such as "math" or "datetime"
        """
        pass

    def pip_install_import(self):
        # later
        """
        other libs, like pandas, or sckitlearn, need to be pip installed.
        """
        pass

    def program_with_mutations(self):
        """
        WAIT: need types to be more stable for representing mutation
        """
        pass

    def program_with_loops(self):
        pass

    def program_with_conditionals(self):
        pass
