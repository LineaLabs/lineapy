import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_statement",
)
literal_1 = LiteralNode(
    value="""class A():
    def __init__(self, initialname:str):
        self.varname = initialname
    def update_name(newname:str):
        self.varname = newname""",
)
lookup_2 = LookupNode(
    name="getattr",
)
lookup_3 = LookupNode(
    name="l_exec_statement",
)
literal_2 = LiteralNode(
    value="""class Modifier():
    def modify_A(self,classinstance):
        classinstance.varname = new_value""",
)
literal_3 = LiteralNode(
    value="modify_A",
)
source_1 = SourceCode(
    code="""new_value="newval"
class A():
    def __init__(self, initialname:str):
        self.varname = initialname
    def update_name(newname:str):
        self.varname = newname

class Modifier():
    def modify_A(self,classinstance):
        classinstance.varname = new_value

a = A("origvalue")
b = Modifier()
b.modify_A(a)
""",
    location=PosixPath("[source file path]"),
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=10,
        end_lineno=1,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value="newval",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=6,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
global_1 = GlobalNode(
    name="A",
    call_id=call_1.id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=10,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_2.id],
)
global_2 = GlobalNode(
    name="Modifier",
    call_id=call_2.id,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=6,
        end_lineno=12,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    value="origvalue",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=4,
        end_lineno=12,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    positional_args=[literal_5.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=13,
        col_offset=4,
        end_lineno=13,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=global_2.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=14,
        col_offset=0,
        end_lineno=14,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_4.id, literal_3.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=14,
        col_offset=0,
        end_lineno=14,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[call_3.id],
    global_reads={"new_value": literal_4.id},
)
