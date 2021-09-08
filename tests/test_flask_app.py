# set up the database with stub data for testing/debugging
import os.path as path
from uuid import UUID

import pytest

from lineapy import ExecutionMode
import lineapy.app.app_db
from lineapy.db.base import LineaDBConfig, get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB


@pytest.fixture(autouse=True)
def test_db_mock(monkeypatch):
    test_db = setup_db(ExecutionMode.TEST)
    monkeypatch.setattr(lineapy.app.app_db, "lineadb", test_db)


# NOTE: @Yifan please uncomment this test when you've implemented line and column numbers in transformer
# def test_executor_and_db_apis(test_db_mock):
#     from lineapy.app.app_db import lineadb

#     s = lineadb.data_asset_manager.read_node_value(
#         UUID("ccebc2e9-d710-4943-8bae-947fa1492d7f"), 1
#     )
#     assert s == 25


def setup_db(mode: ExecutionMode):
    test_db = RelationalLineaDB()
    db_config = get_default_config_by_environment(mode)
    test_db.init_db(db_config)

    setup_value_test(test_db, mode)
    setup_image_test(test_db, mode)


def setup_value_test(test_db: RelationalLineaDB, mode: ExecutionMode):
    from lineapy.execution.executor import Executor
    from lineapy.db.relational.schema.relational import (
        ExecutionORM,
    )
    from lineapy.data.types import VALUE_TYPE

    from tests.stub_data.api_stub_graph import (
        graph_with_csv_import as stub_graph,
        session as context,
        sum_call as artifact,
        simple_data_node,
    )

    from tests.util import get_new_id

    if mode == ExecutionMode.DEV:
        simple_data_node.access_path = (
            path.abspath(path.join(__file__, "../.."))
            + "/tests/stub_data/simple_data.csv"
        )

    executor = Executor()

    # execute stub graph and write to database
    executor.execute_program(stub_graph, context)
    test_db.write_context(context)
    test_db.write_nodes(stub_graph.nodes)

    test_db.add_node_id_to_artifact_table(
        artifact.id,
        context_id=context.id,
        value_type=VALUE_TYPE,
        name="Graph With CSV Import",
        date_created="1372944000",
    )

    exec_orm = ExecutionORM(artifact_id=artifact.id, version=1)
    test_db.session.add(exec_orm)
    test_db.session.commit()


def setup_image_test(test_db: RelationalLineaDB, mode: ExecutionMode):
    from lineapy.execution.executor import Executor
    from lineapy.db.relational.schema.relational import ExecutionORM
    from lineapy.data.types import CHART_TYPE

    from tests.stub_data.graph_with_basic_image import (
        graph_with_basic_image as stub_graph,
        session as context,
        read_call,
        simple_data_node,
        img_data_node,
    )

    from tests.util import get_new_id

    if mode == ExecutionMode.DEV:
        simple_data_node.access_path = (
            path.abspath(path.join(__file__, "../.."))
            + "/tests/stub_data/simple_data.csv"
        )

        img_data_node.access_path = (
            path.abspath(path.join(__file__, "../..")) + "/lineapy/app/simple_data.png"
        )

    executor = Executor()

    # execute stub graph and write to database
    executor.execute_program(stub_graph, context)
    test_db.write_context(context)
    test_db.write_nodes(stub_graph.nodes)

    test_db.add_node_id_to_artifact_table(
        read_call.id,
        context_id=context.id,
        value_type=CHART_TYPE,
        name="Graph With Image",
        date_created="1372944000",
    )

    exec_orm = ExecutionORM(artifact_id=read_call.id, version=1)
    test_db.session.add(exec_orm)
    test_db.session.commit()
