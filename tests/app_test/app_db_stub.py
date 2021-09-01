from lineapy.db.db import LineaDB
from lineapy.db.base import LineaDBConfig


def init_db(app):
    print("🛠", app.config)
    # TODO: pass app.config into LineaDBConfig
    global lineadb
    lineadb = LineaDB(LineaDBConfig())
    setup_tests()


# set up the database with stub data for testing/debugging
def setup_tests():
    from lineapy.execution.executor import Executor
    from lineapy.data.types import DataAssetType

    from tests.stub_data.api_stub_graph import (
        graph_with_csv_import as stub_graph,
        session as context,
        sum_call,
    )

    executor = Executor()

    # execute stub graph and write to database
    executor.execute_program(stub_graph)
    lineadb.write_context(context)
    lineadb.write_nodes(stub_graph._nodes)

    # TODO: determine type of artifact view
    lineadb.add_node_id_to_artifact_table(
        sum_call.id, context_id=context.id, value_type=DataAssetType.Value
    )
