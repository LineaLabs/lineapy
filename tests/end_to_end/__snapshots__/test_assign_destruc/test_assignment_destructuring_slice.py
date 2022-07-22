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
lookup_3 = LookupNode(
    name="l_unpack_sequence",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="save",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value=1,
)
literal_4 = LiteralNode(
    value="lineapy",
)
literal_5 = LiteralNode(
    value=0,
)
lookup_5 = LookupNode(
    name="getitem",
)
lookup_6 = LookupNode(
    name="getattr",
)
literal_6 = LiteralNode(
    value=2,
)
lookup_7 = LookupNode(
    name="getitem",
)
literal_7 = LiteralNode(
    value="save",
)
lookup_8 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
c = [1,2]
a, b = c
lineapy.save(a, "a")
lineapy.save(b, "b")
lineapy.save(c, "c")
""",
    location=PosixPath("[source file path]"),
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
    positional_args=[literal_4.id],
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
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=1,
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=7,
        end_lineno=2,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value=2,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_8.id, literal_9.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_2.id, literal_6.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_3.id, literal_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_3.id, literal_5.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=16,
        end_lineno=4,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[call_5.id, literal_10.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_1.id, literal_7.id],
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=16,
        end_lineno=5,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="b",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[call_4.id, literal_11.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_12 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=16,
        end_lineno=6,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="c",
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_10.id,
    positional_args=[call_2.id, literal_12.id],
)
