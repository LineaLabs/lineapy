import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
literal_1 = LiteralNode(
    value="lambda x: a + x",
)
lookup_2 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="lineapy",
)
lookup_3 = LookupNode(
    name="l_exec_expr",
)
lookup_4 = LookupNode(
    name="l_list",
)
source_1 = SourceCode(
    code="""import lineapy
a = 10
fn = lambda x: a + x
r = sum(map(fn, [1]))

lineapy.save(r, \'r\')
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
    positional_args=[literal_3.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=5,
        end_lineno=3,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_1.id],
)
lookup_5 = LookupNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="sum",
)
lookup_6 = LookupNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    name="map",
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=17,
        end_lineno=4,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value=1,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=16,
        end_lineno=4,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_5.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_2.id, call_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_4.id],
    global_reads={"a": literal_4.id},
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=16,
        end_lineno=6,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="r",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[call_5.id, literal_6.id],
)
