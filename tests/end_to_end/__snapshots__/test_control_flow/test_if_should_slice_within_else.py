import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="le",
)
literal_1 = LiteralNode(
    value="save",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="lineapy",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
a = 10
b = 20
if a <= 5:
    a = 5
    b = 5
else:
    a = 100
    b = 101

lineapy.save(a, \'a\')
lineapy.save(b, \'b\')
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
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=20,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=5,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=3,
        end_lineno=4,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_4.id, literal_6.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=6,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value="""a = 5
b = 5""",
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=3,
        end_lineno=4,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    companion_id=else_1.id,
    unexec_id=literal_7.id,
    test_id=call_2.id,
)
else_1 = ElseNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=4,
        source_code=source_1.id,
    ),
    companion_id=if_1.id,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=8,
        end_lineno=8,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
    value=100,
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=8,
        end_lineno=9,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
    value=101,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=16,
        end_lineno=11,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_8.id, literal_10.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=16,
        end_lineno=12,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="b",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[literal_9.id, literal_11.id],
)
