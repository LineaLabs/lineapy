import unittest
from typing import Tuple

from lineapy import ExecutionMode
from lineapy.utils import get_current_time
from lineapy.data.graph import Graph
from lineapy.data.types import SessionContext
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.execution.executor import Executor
from lineapy.graph_reader.graph_util import are_graphs_identical
from lineapy.graph_reader.graph_util import are_nodes_equal
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
    simple_data_node,
    sum_call,
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
    y_id,
    code as loops_code,
)
from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    graph_sliced_by_var_f,
    session as graph_with_messy_nodes_session,
    f_assign,
    sliced_code,
)
from tests.stub_data.nested_call_graph import (
    code as nested_call_graph_code,
)

from tests.stub_data.simple_with_variable_argument_and_print import (
    code as print_code,
)
from tests.util import are_str_equal, reset_test_db


class TestLineaDB:
    @property
    def db_config(self):
        return get_default_config_by_environment(ExecutionMode.MEMORY)

    def setup_method(self):
        # just use the default config
        self.lineadb = RelationalLineaDB()
        self.lineadb.init_db(self.db_config)

    def teardown_method(self):
        # remove the test db
        reset_test_db(self.db_config.database_uri)

    def write_and_read_graph(
        self,
        graph: Graph,
        context: SessionContext,
    ) -> Tuple[Graph, SessionContext]:
        # let's write the in memory graph in (with all the nodes)
        self.lineadb.write_nodes(graph.nodes)
        self.lineadb.write_context(context)

        graph_from_db = self.reconstruct_graph(graph)
        session_from_db = self.lineadb.get_context(context.id)
        return graph_from_db, session_from_db

    def reconstruct_graph(self, original_graph: Graph) -> Graph:
        # let's then read some nodes back
        nodes = []
        for reference in original_graph.nodes:
            node = self.lineadb.get_node_by_id(reference.id)
            nodes.append(node)
            assert are_nodes_equal(reference, node, True)

        db_graph = Graph(nodes)

        return db_graph

    def test_nested_call_graph(self, execute):
        assert execute(nested_call_graph_code).values["a"] == 10

    def test_graph_with_print(self, execute):
        assert execute(print_code).stdout == "10\n"

    def test_basic_import(self, execute):
        """
        some imports are built in, such as "math" or "datetime"
        """
        assert execute(graph_with_import_code).values["b"] == 5

    # TODO: Move to E2E when function definitions that edit globals work
    def test_graph_with_function_definition(self, execute):
        """ """
        graph, context = self.write_and_read_graph(
            graph_with_function_definition,
            graph_with_function_definition_session,
        )
        e = Executor()
        e.execute_program(graph, context)
        a = e.get_value_by_variable_name("a")
        assert a == 120
        assert are_graphs_identical(graph, graph_with_function_definition)

    # TODO: Move to E2E when control flow works
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

    # TODO: Move to E2E when control flow works
    def test_program_with_conditionals(self):
        graph, context = self.write_and_read_graph(
            graph_with_conditionals,
            graph_with_conditionals_session,
        )
        e = Executor()
        e.execute_program(graph, context)
        bs = e.get_value_by_variable_name("bs")
        stdout = e.get_stdout()
        assert bs == [1, 2, 3]
        assert stdout == "False\n"
        assert are_graphs_identical(graph, graph_with_conditionals)

    # TODO: Move to e2e when https://github.com/LineaLabs/lineapy/issues/178 is fixed
    def test_program_with_file_access(self):
        graph, context = self.write_and_read_graph(
            graph_with_csv_import, graph_with_file_access_session
        )
        e = Executor()
        e.execute_program(graph, context)
        s = e.get_value_by_variable_name("s")
        assert s == 25
        assert are_graphs_identical(graph, graph_with_csv_import)

        # test search_artifacts_by_data_source
        time = get_current_time()
        self.lineadb.add_node_id_to_artifact_table(
            sum_call.id,
            time,
        )
        derived = self.lineadb.find_all_artifacts_derived_from_data_source(
            graph, simple_data_node
        )
        assert len(derived) == 1
        assert derived

    # TODO:  Move to e2e when https://github.com/LineaLabs/lineapy/issues/155 is fixed
    def test_variable_alias_by_value(self):
        graph, context = self.write_and_read_graph(
            graph_with_alias_by_value, graph_with_alias_by_value_session
        )
        e = Executor()
        e.execute_program(graph, context)
        a = e.get_value_by_variable_name("a")
        b = e.get_value_by_variable_name("b")
        assert a == 2
        assert b == 0
        assert are_graphs_identical(graph, graph_with_alias_by_value)

    # TODO:  Move to e2e when https://github.com/LineaLabs/lineapy/issues/155 is fixed
    def test_variable_alias_by_reference(self):
        graph, context = self.write_and_read_graph(
            graph_with_alias_by_reference,
            graph_with_alias_by_reference_session,
        )
        e = Executor()
        e.execute_program(graph, context)
        s = e.get_value_by_variable_name("s")
        assert s == 10
        assert are_graphs_identical(graph, graph_with_alias_by_reference)

    # TODO:  Move to e2e when https://github.com/LineaLabs/lineapy/issues/155 is fixed
    def test_slicing(self):
        graph, context = self.write_and_read_graph(
            graph_with_messy_nodes, graph_with_messy_nodes_session
        )
        self.lineadb.add_node_id_to_artifact_table(
            f_assign.id,
            get_current_time(),
        )
        result = self.lineadb.get_graph_from_artifact_id(f_assign.id)
        self.lineadb.remove_node_id_from_artifact_table(f_assign.id)
        e = Executor()
        e.execute_program(result, context)
        f = e.get_value_by_variable_name("f")
        assert f == 6
        assert are_graphs_identical(result, graph_sliced_by_var_f)

    # TODO: Move to E2E when control flow works
    def test_slicing_loops(self):
        graph, context = self.write_and_read_graph(
            graph_with_loops, graph_with_loops_session
        )
        self.lineadb.add_node_id_to_artifact_table(
            y_id,
            get_current_time(),
        )
        result = self.lineadb.get_graph_from_artifact_id(y_id)
        assert are_graphs_identical(result, graph)

    # TODO: Move to E2E when control flow works
    def test_code_reconstruction_with_multilined_node(self):
        _ = self.write_and_read_graph(
            graph_with_loops,
            graph_with_loops_session,
        )

        self.lineadb.add_node_id_to_artifact_table(
            y_id,
            get_current_time(),
        )
        reconstructed = self.lineadb.get_code_from_artifact_id(y_id)

        assert are_str_equal(loops_code, reconstructed)

    # TODO: Move to E2E when control flow works
    def test_code_reconstruction_with_slice(self):
        _ = self.write_and_read_graph(
            graph_with_messy_nodes, graph_with_messy_nodes_session
        )

        self.lineadb.add_node_id_to_artifact_table(
            f_assign.id,
            get_current_time(),
        )
        reconstructed = self.lineadb.get_code_from_artifact_id(f_assign.id)
        assert are_str_equal(sliced_code, reconstructed)
