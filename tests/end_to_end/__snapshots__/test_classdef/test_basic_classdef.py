import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_exec_statement",
)
literal_1 = LiteralNode(
    value="""class A():
    def __init__(self, varname:str):
        self.varname = varname""",
)
source_1 = SourceCode(
    code="""class A():
    def __init__(self, varname:str):
        self.varname = varname
a = A("myclass")
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=3,
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
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=6,
        end_lineno=4,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    value="myclass",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    positional_args=[literal_2.id],
)
