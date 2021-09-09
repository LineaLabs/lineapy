import os.path as path
from ast import AST
from datetime import datetime
from os import remove
from typing import Optional, List

from astpretty import pformat

import lineapy
import lineapy.app.app_db
from lineapy import ExecutionMode
from lineapy.data.types import (
    SessionContext,
    SessionType,
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.utils import get_new_id


def get_new_session(code: str, libraries: Optional[List] = None) -> SessionContext:
    if libraries is None:
        libraries = []
    return SessionContext(
        id=get_new_id(),
        file_name="testing.py",
        environment_type=SessionType.SCRIPT,
        creation_time=datetime.now(),
        libraries=libraries,
        code=code,
    )


def reset_test_db(sqlite_uri: str):
    """ """
    try:
        r = sqlite_uri.split("///")
        remove(r[1])
        return True
    except:
        return False


def compare_ast(node1: AST, node2: AST):
    """
    Compare two AST trees, ignoring offset information.
    """
    s1 = pformat(node1, show_offsets=False)
    s2 = pformat(node2, show_offsets=False)
    return s1 == s2


def setup_db(mode: ExecutionMode, reset: bool = True):
    test_db = RelationalLineaDB()
    db_config = get_default_config_by_environment(mode)
    if reset:
        reset_test_db(db_config.database_uri)
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

    if mode == "DEV":
        simple_data_node.access_path = path.join(
            path.abspath(lineapy.__file__), "/tests/stub_data/simple_data.csv"
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
