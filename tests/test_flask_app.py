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


def test_executor_and_db_apis(test_db_mock):
    from lineapy.app.app_db import lineadb

    s = lineadb.data_asset_manager.read_node_value(
        UUID("ccebc2e9-d710-4943-8bae-947fa1492d7f"), 1
    )
    assert s == 25


def setup_db(mode: ExecutionMode):
    test_db = RelationalLineaDB()
    db_config = get_default_config_by_environment(mode)
    test_db.init_db(db_config)
    from lineapy.execution.executor import Executor
    from lineapy.db.relational.schema.relational import (
        ExecutionORM,
        CodeORM,
        TokenORM,
        code_token_association_table,
    )
    from lineapy.data.types import VALUE_TYPE

    from tests.stub_data.api_stub_graph import (
        graph_with_csv_import as stub_graph,
        session as context,
        sum_call,
        read_csv_call,
        simple_data_node,
    )
    from tests.util import get_new_id

    if mode == "DEV":
        simple_data_node.access_path = (
            path.abspath(path.join(__file__, "../.."))
            + "/tests/stub_data/simple_data.csv"
        )

    executor = Executor()

    # execute stub graph and write to database
    executor.execute_program(stub_graph)
    test_db.write_context(context)
    test_db.write_nodes(stub_graph.nodes)

    artifact_code = CodeORM(
        id=get_new_id(),
        text="import pandas as pd\ndf = pd.read_csv('simple_data.csv')\ns = df['a'].sum()",
    )

    code_token = TokenORM(
        id=get_new_id(),
        line=2,
        start=1,
        end=3,
        intermediate=read_csv_call.id,
    )

    test_db.session.execute(
        code_token_association_table.insert(),
        params={
            "code": artifact_code.id,
            "token": code_token.id,
        },
    )

    test_db.session.add(artifact_code)
    test_db.session.add(code_token)
    test_db.session.commit()

    test_db.add_node_id_to_artifact_table(
        sum_call.id,
        context_id=context.id,
        value_type=VALUE_TYPE,
        name="Graph With CSV Import",
        date_created="1372944000",
        code=artifact_code.id,
    )

    exec_orm = ExecutionORM(artifact_id=sum_call.id, version=1)
    test_db.session.add(exec_orm)
    test_db.session.commit()
    return test_db
