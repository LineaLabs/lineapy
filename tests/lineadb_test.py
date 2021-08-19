from lineapy.db.db import LineaDB
from lineapy.graph_reader.graph_util import are_nodes_equal
from lineapy.db.base import LineaDBConfig
from tests.stub_data.simple_graph import simple_graph
from tests.stub_data.graph_with_messy_nodes import (
    graph_with_messy_nodes,
    graph_sliced_by_var_f,
)
from tests.util import reset_test_db


class TestLineaDB:
    """
    Maybe we should wrap this in the unit test class?
    """

    def set_up(self):
        # just use the default config
        self.lineadb = LineaDB(LineaDBConfig())

    def test_writing_and_reading_simple_graph_nodes(self):
        # # let's write the in memory graph in (with all the nodes)
        # self.lineadb.write_nodes(simple_graph_nodes)
        # # lets then read some nodes back
        # for reference in simple_graph_nodes:
        #     result = self.lineadb.get_node_by_id(reference.id)
        #     assert are_nodes_equal(reference, result, True)
        pass

    def test_slicing(self):
        # self.lineadb.write_nodes(graph_with_messy_nodes)
        # result = self.lineadb.get_graph_from_artifact_id()
        # graph_sliced_by_var_f
        pass

    # TODO: please add the test for all the other graphs that we have stubbed

    def test_search_artifacts_by_data_source(self):
        # TODO
        # @dhruv we should create at least one more stub_graph with the same csv file ("sample_data.csv")---it's currently not in this branch but we can merge master in here later.
        pass

    def tear_down(self):
        # remove the test db
        # @dorx, please share what the best way to do a tear down is---I think having a delete_db function on LineaDBWriter seems a little dangerous?
        reset_test_db()
        pass


if __name__ == "__main__":
    tester = TestLineaDB()
    tester.set_up()
    tester.test_writing_and_reading_simple_graph_nodes()
    tester.test_search_artifacts_by_data_source()
    tester.tear_down()
