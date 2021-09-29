import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import lineapy\nfrom PIL.Image import open\n\nimg = open('simple_data.png')\nimg = img.resize([200, 200])\n\nlineapy.linea_publish(img, \"Graph With Image\")\n",
    working_directory="dummy_linea_repo/",
    libraries=[
        Library(
            id=get_new_id(),
            name="PIL.Image",
        ),
        Library(
            id=get_new_id(),
            name="lineapy",
        ),
    ],
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="open",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="__build_list__",
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="resize",
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=14,
    library=Library(
        id=get_new_id(),
        name="lineapy",
    ),
)
import_2 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=26,
    library=Library(
        id=get_new_id(),
        name="PIL.Image",
    ),
    attributes={"open": "open"},
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=11,
    end_lineno=4,
    end_col_offset=28,
    value="simple_data.png",
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=18,
    end_lineno=5,
    end_col_offset=21,
    value=200,
)
literal_5 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=23,
    end_lineno=5,
    end_col_offset=26,
    value=200,
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_1.id,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=import_2.id,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_3.id,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_4.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_5.id,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_2.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=17,
    end_lineno=5,
    end_col_offset=27,
    arguments=[argument_4.id, argument_5.id],
    function_id=lookup_2.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="open",
)
argument_7 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_2.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=29,
    arguments=[argument_3.id],
    function_id=variable_1.id,
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_3.id,
    assigned_variable_name="img",
)
argument_8 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_2.id,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=6,
    end_lineno=5,
    end_col_offset=16,
    arguments=[argument_6.id, argument_8.id],
    function_id=lookup_3.id,
)
call_5 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=0,
    end_lineno=5,
    end_col_offset=28,
    arguments=[argument_7.id],
    function_id=call_4.id,
)
variable_3 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_5.id,
    assigned_variable_name="img",
)
