import os.path as path
from ast import AST
from datetime import datetime
from os import remove
from typing import Optional, List
from re import sub
from astpretty import pformat

import lineapy.app.app_db
from lineapy import ExecutionMode
from lineapy.data.types import (
    SessionContext,
    SessionType,
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.utils import get_new_id


def strip_non_letter_num(s: str):
    return sub("[\\s+]", "", s)


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


def setup_db(mode: ExecutionMode, reset: bool):
    test_db = RelationalLineaDB()
    db_config = get_default_config_by_environment(mode)
    if reset:
        reset_test_db(db_config.database_uri)
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

    if mode == ExecutionMode.DEV:
        simple_data_node.access_path = (
            path.abspath(path.join(__file__, "../.."))
            + "/tests/stub_data/simple_data.csv"
        )

    executor = Executor()

    # execute stub graph and write to database
    execution_time = executor.execute_program(stub_graph, context)
    test_db.write_context(context)
    test_db.write_nodes(stub_graph.nodes)

    test_db.add_node_id_to_artifact_table(
        artifact.id,
        name="Graph With CSV Import",
        date_created=1372944000.0,
    )

    exec_orm = ExecutionORM(
        artifact_id=artifact.id, version=1, execution_time=execution_time
    )
    test_db.session.add(exec_orm)
    test_db.session.commit()


def setup_image_test(test_db: RelationalLineaDB, mode: ExecutionMode):
    from lineapy.execution.executor import Executor
    from lineapy.db.relational.schema.relational import ExecutionORM
    from lineapy.data.types import CHART_TYPE

    from tests.stub_data.graph_with_basic_image import (
        graph_with_basic_image as stub_graph,
        session as context,
        resize_call,
        simple_data_node,
        img_data_node,
    )

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
    execution_time = executor.execute_program(stub_graph, context)
    test_db.write_context(context)
    test_db.write_nodes(stub_graph.nodes)

    test_db.add_node_id_to_artifact_table(
        resize_call.id,
        name="Graph With Image",
        date_created=1372944000.0,
    )

    exec_orm = ExecutionORM(
        artifact_id=resize_call.id, version=1, execution_time=execution_time
    )
    test_db.session.add(exec_orm)
    test_db.session.commit()
