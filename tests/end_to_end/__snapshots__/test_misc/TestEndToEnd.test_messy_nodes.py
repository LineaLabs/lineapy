import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="add",
)
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="l_alias",
)
literal_1 = LiteralNode(
    value="lineapy",
)
lookup_5 = LookupNode(
    name="mul",
)
lookup_6 = LookupNode(
    name="mul",
)
lookup_7 = LookupNode(
    name="add",
)
literal_2 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
a = 1
b = a + 2
c = 2
d = 4
e = d + a
f = a * b * c
10
e
g = e

lineapy.save(f, \'f\')
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
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=1,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=8,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=2,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=2,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=4,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_6.id, literal_3.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_3.id, call_2.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_4.id, literal_5.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=2,
        source_code=source_1.id,
    ),
    value=10,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_3.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=16,
        end_lineno=12,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="f",
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_7.id,
    positional_args=[call_5.id, literal_8.id],
)
