from lineapy.db.base import LineaDBConfig
from lineapy.db.relational.db import RelationalLineaDB

lineadb = RelationalLineaDB(LineaDBConfig())


def init_db(app):
    print("🛠", app.config)
    # TODO: set LineaDBConfig to be app.config
    if app.config["DEBUG"]:
        setup_tests()


def setup_tests():
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
    )
    from tests.util import get_new_id

    executor = Executor()

    # execute stub graph and write to database
    executor.execute_program(stub_graph)
    lineadb.write_context(context)
    lineadb.write_nodes(stub_graph._nodes)

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

    lineadb.session.execute(
        code_token_association_table.insert(),
        params={
            "code": artifact_code.id,
            "token": code_token.id,
        },
    )

    lineadb.session.add(artifact_code)
    lineadb.session.add(code_token)
    lineadb.session.commit()

    lineadb.add_node_id_to_artifact_table(
        sum_call.id,
        context_id=context.id,
        value_type=VALUE_TYPE,
        name="Graph With CSV Import",
        date_created="1372944000",
        code=artifact_code.id,
    )

    exec_orm = ExecutionORM(artifact_id=sum_call.id, version=1)
    lineadb.session.add(exec_orm)
    lineadb.session.commit()
