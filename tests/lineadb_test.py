from lineapy.data.graph import Graph
from lineapy.data.types import SessionContext
from lineapy.db.base import LineaDBConfig
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.graph_reader.graph_util import are_graphs_identical
from lineapy.graph_reader.graph_util import are_nodes_equal
from tests.stub_data.graph_with_alias_by_reference import graph_with_alias_by_reference
from tests.stub_data.graph_with_alias_by_value import graph_with_alias_by_value
from tests.stub_data.graph_with_conditionals import graph_with_conditionals
from tests.stub_data.graph_with_csv_import import (
    graph_with_csv_import,
    session as graph_with_file_access_session,
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
from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    graph_sliced_by_var_f,
    session as graph_with_messy_nodes_session,
    f_assign,
    e_assign,
    a_assign,
)
from tests.stub_data.nested_call_graph import nested_call_graph
from tests.stub_data.simple_graph import simple_graph
from tests.stub_data.simple_with_variable_argument_and_print import (
    simple_with_variable_argument_and_print,
)
from tests.util import reset_test_db


class TestLineaDB:
    """
    Maybe we should wrap this in the unit test class?
    """

    def set_up(self):
        # just use the default config
        self.lineadb = RelationalLineaDB(LineaDBConfig())

    def write_and_read_graph(
        self, graph: Graph, context: SessionContext = None
    ) -> Graph:
        # let's write the in memory graph in (with all the nodes)
        self.lineadb = RelationalLineaDB(LineaDBConfig())
        self.lineadb.write_nodes(graph.nodes)

        if context is not None:
            self.lineadb.write_context(context)

        if context is not None:
            return self.reconstruct_graph(graph), self.lineadb.get_context(context.id)
        return self.reconstruct_graph(graph)

    def reconstruct_graph(self, original_graph: Graph) -> Graph:
        # let's then read some nodes back
        nodes = []
        for reference in original_graph.nodes:
            node = self.lineadb.get_node_by_id(reference.id)
            nodes.append(node)
            assert are_nodes_equal(reference, node, True)

        db_graph = Graph(nodes)

        return db_graph

    def test_simple_graph(self):
        graph = self.write_and_read_graph(simple_graph)
        e = Executor()
        e.execute_program(graph)
        a = e.get_value_by_variable_name("a")
        assert a == 11
        assert are_graphs_identical(graph, simple_graph)

    def test_nested_call_graph(self):
        graph = self.write_and_read_graph(nested_call_graph)
        e = Executor()
        e.execute_program(graph)
        a = e.get_value_by_variable_name("a")
        assert a == 10
        assert are_graphs_identical(graph, nested_call_graph)

    def test_graph_with_print(self):
        graph = self.write_and_read_graph(simple_with_variable_argument_and_print)
        e = Executor()
        e.execute_program(graph)
        stdout = e.get_stdout()
        assert stdout == "10\n"
        assert are_graphs_identical(graph, simple_with_variable_argument_and_print)

    def test_basic_import(self):
        """
        some imports are built in, such as "math" or "datetime"
        """
        graph, context = self.write_and_read_graph(
            graph_with_import, graph_with_import_session
        )
        e = Executor()
        e.execute_program(graph, context)
        b = e.get_value_by_variable_name("b")
        assert b == 5
        assert are_graphs_identical(graph, graph_with_import)

    def test_graph_with_function_definition(self):
        """ """
        graph, context = self.write_and_read_graph(
            graph_with_function_definition, graph_with_function_definition_session
        )
        e = Executor()
        e.execute_program(graph, context)
        a = e.get_value_by_variable_name("a")
        assert a == 120
        assert are_graphs_identical(graph, graph_with_function_definition)

    def test_program_with_loops(self):
        graph, context = self.write_and_read_graph(
            graph_with_loops, graph_with_loops_session
        )
        e = Executor()
        e.execute_program(graph, context)
        y = e.get_value_by_variable_name("y")
        x = e.get_value_by_variable_name("x")
        a = e.get_value_by_variable_name("a")
        assert y == 72
        assert x == 36
        assert len(a) == 9
        assert are_graphs_identical(graph, graph_with_loops)

    def test_program_with_conditionals(self):
        graph = self.write_and_read_graph(graph_with_conditionals)
        e = Executor()
        e.execute_program(graph)
        bs = e.get_value_by_variable_name("bs")
        stdout = e.get_stdout()
        assert bs == [1, 2, 3]
        assert stdout == "False\n"
        assert are_graphs_identical(graph, graph_with_conditionals)

    def test_program_with_file_access(self):
        graph, context = self.write_and_read_graph(
            graph_with_csv_import, graph_with_file_access_session
        )
        e = Executor()
        e.execute_program(graph, context)
        s = e.get_value_by_variable_name("s")
        assert s == 25
        assert are_graphs_identical(graph, graph_with_csv_import)

    def test_variable_alias_by_value(self):
        graph = self.write_and_read_graph(graph_with_alias_by_value)
        e = Executor()
        e.execute_program(graph)
        a = e.get_value_by_variable_name("a")
        b = e.get_value_by_variable_name("b")
        assert a == 2
        assert b == 0
        assert are_graphs_identical(graph, graph_with_alias_by_value)

    def test_variable_alias_by_reference(self):
        graph = self.write_and_read_graph(graph_with_alias_by_reference)
        e = Executor()
        e.execute_program(graph)
        s = e.get_value_by_variable_name("s")
        assert s == 10
        assert are_graphs_identical(graph, graph_with_alias_by_reference)

    def test_slicing(self):
        self.write_and_read_graph(
            graph_with_messy_nodes, graph_with_messy_nodes_session
        )
        self.lineadb.add_node_id_to_artifact_table(
            f_assign.id,
            graph_with_messy_nodes_session.id,
        )
        result = self.lineadb.get_graph_from_artifact_id(f_assign.id)
        self.lineadb.remove_node_id_from_artifact_table(f_assign.id)
        e = Executor()
        e.execute_program(result)
        f = e.get_value_by_variable_name("f")
        assert f == 6
        assert are_graphs_identical(result, graph_sliced_by_var_f)

    def test_search_artifacts_by_data_source(self):
        # @dhruv we should create at least one more stub_graph with the same csv file ("sample_data.csv")---it's currently not in this branch but we can merge master in here later.
        # using an existing stub for now
        graph, context = self.write_and_read_graph(
            graph_with_messy_nodes, graph_with_messy_nodes_session
        )
        self.lineadb.add_node_id_to_artifact_table(
            f_assign.id, graph_with_messy_nodes_session.id
        )
        self.lineadb.add_node_id_to_artifact_table(
            e_assign.id, graph_with_messy_nodes_session.id
        )
        derived = self.lineadb.find_all_artifacts_derived_from_data_source(
            graph, a_assign
        )
        assert len(derived) == 2

    def tear_down(self):
        # remove the test db
        # @dorx, please share what the best way to do a tear down is---I think having a delete_db function on LineaDBWriter seems a little dangerous?
        reset_test_db()
        pass


if __name__ == "__main__":
    tester = TestLineaDB()
    tester.test_writing_and_reading_simple_graph_nodes()
    tester.test_search_artifacts_by_data_source()
    tester.tear_down()
