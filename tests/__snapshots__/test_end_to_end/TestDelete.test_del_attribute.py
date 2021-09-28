import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import types; x = types.SimpleNamespace(); x.hi = 1; del x.hi",
    working_directory="dummy_linea_repo/",
    session_name=None,
    user_name=None,
    hardware_spec=None,
    libraries=[
        Library(
            id=get_new_id(),
            name="types",
            version=None,
            path=None,
        ),
    ],
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=12,
    library=Library(
        id=get_new_id(),
        name="types",
        version=None,
        path=None,
    ),
    attributes=None,
    alias=None,
    module=None,
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    name="getattr",
    value=None,
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    value="SimpleNamespace",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    name="setattr",
    value=None,
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    value="hi",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=50,
    end_lineno=1,
    end_col_offset=51,
    value=1,
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    name="delattr",
    value=None,
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    value="hi",
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
    value_node_id=import_1.id,
    value_literal=None,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=1,
    value_node_id=literal_1.id,
    value_literal=None,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=1,
    value_node_id=literal_2.id,
    value_literal=None,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=2,
    value_node_id=literal_3.id,
    value_literal=None,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=1,
    value_node_id=literal_4.id,
    value_literal=None,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=18,
    end_lineno=1,
    end_col_offset=39,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
    value=None,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=14,
    end_lineno=1,
    end_col_offset=41,
    arguments=[],
    function_id=call_1.id,
    value=None,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    source_node_id=call_2.id,
    assigned_variable_name="x",
    value=None,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
    value_node_id=variable_1.id,
    value_literal=None,
)
argument_7 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
    value_node_id=variable_1.id,
    value_literal=None,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=43,
    end_lineno=1,
    end_col_offset=51,
    arguments=[argument_3.id, argument_4.id, argument_6.id],
    function_id=lookup_2.id,
    value=None,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=53,
    end_lineno=1,
    end_col_offset=61,
    arguments=[argument_5.id, argument_7.id],
    function_id=lookup_3.id,
    value=None,
)
