import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import pandas as pd\nimport lineapy\n\ndf = pd.read_csv('tests/simple_data.csv')\ns = df['a'].sum()\n\nlineapy.linea_publish(s, \"Graph With CSV Import\")\n",
    working_directory="dummy_linea_repo/",
    libraries=[
        Library(
            id=get_new_id(),
            name="lineapy",
        ),
        Library(
            id=get_new_id(),
            name="pandas",
        ),
    ],
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=19,
    library=Library(
        id=get_new_id(),
        name="pandas",
    ),
    alias="pd",
)
import_2 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=14,
    library=Library(
        id=get_new_id(),
        name="lineapy",
    ),
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=17,
    end_lineno=4,
    end_col_offset=40,
    value="tests/simple_data.csv",
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="read_csv",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=7,
    end_lineno=5,
    end_col_offset=10,
    value="a",
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getitem",
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="sum",
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=import_1.id,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_1.id,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_2.id,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_3.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_4.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=5,
    end_lineno=4,
    end_col_offset=16,
    arguments=[argument_1.id, argument_3.id],
    function_id=lookup_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=41,
    arguments=[argument_2.id],
    function_id=call_1.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_2.id,
    assigned_variable_name="df",
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_1.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=4,
    end_lineno=5,
    end_col_offset=11,
    arguments=[argument_4.id, argument_6.id],
    function_id=lookup_3.id,
)
argument_7 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_3.id,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=4,
    end_lineno=5,
    end_col_offset=15,
    arguments=[argument_5.id, argument_7.id],
    function_id=lookup_2.id,
)
call_5 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=0,
    end_lineno=5,
    end_col_offset=17,
    arguments=[],
    function_id=call_4.id,
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_5.id,
    assigned_variable_name="s",
)
