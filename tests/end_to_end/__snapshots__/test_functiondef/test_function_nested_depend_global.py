import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
literal_1 = LiteralNode(
    value="lineapy",
)
literal_2 = LiteralNode(
    value="""def foo():
    def inner():
        return a
    return inner""",
)
literal_3 = LiteralNode(
    value="save",
)
lookup_2 = LookupNode(
    name="l_exec_statement",
)
lookup_3 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
def foo():
    def inner():
        return a
    return inner
a = 10
c = foo()()

lineapy.save(c, \'c\')
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
    positional_args=[literal_1.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=5,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_2.id],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_2.id,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    global_reads={"a": literal_4.id},
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=16,
        end_lineno=9,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="c",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[call_4.id, literal_5.id],
)
