import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_list",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="lineapy",
)
literal_3 = LiteralNode(
    value="""def f():
    a.append(1)""",
)
lookup_3 = LookupNode(
    name="l_exec_statement",
)
lookup_4 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
def f():
    a.append(1)
a = []
f()

lineapy.save(a, \'a\')
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    name="lineapy",
    version="",
    package_name="lineapy",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_3.id],
)
global_1 = GlobalNode(
    name="f",
    call_id=call_2.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=3,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    global_reads={"a": call_3.id},
)
mutate_1 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=16,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[mutate_1.id, literal_4.id],
)
