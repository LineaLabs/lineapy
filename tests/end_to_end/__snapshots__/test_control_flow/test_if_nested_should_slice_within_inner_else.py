import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="gt",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="lineapy",
)
lookup_3 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
a = 10
b = 20
if a > 0:
    if a <= 2:
        a = 1
        b = 2
    else:
        a = 3
        b = 4
else:
    a = 5
    b = 6

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
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=20,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=7,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value=0,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=3,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_5.id],
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=3,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    companion_id=else_1.id,
    test_id=call_2.id,
)
lookup_4 = LookupNode(
    control_dependency=if_1.id,
    name="le",
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=12,
        end_lineno=5,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    value=2,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=7,
        end_lineno=5,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    function_id=lookup_4.id,
    positional_args=[literal_3.id, literal_6.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=8,
        end_lineno=7,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    value="""a = 1
b = 2""",
)
if_2 = IfNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=7,
        end_lineno=5,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    companion_id=else_2.id,
    unexec_id=literal_7.id,
    test_id=call_3.id,
)
else_2 = ElseNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    companion_id=if_2.id,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=12,
        end_lineno=9,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=else_2.id,
    value=3,
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=12,
        end_lineno=10,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=else_2.id,
    value=4,
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=4,
        end_lineno=13,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value="""a = 5
b = 6""",
)
else_1 = ElseNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=4,
        source_code=source_1.id,
    ),
    companion_id=if_1.id,
    unexec_id=literal_10.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=15,
        col_offset=0,
        end_lineno=15,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=15,
        col_offset=16,
        end_lineno=15,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=15,
        col_offset=0,
        end_lineno=15,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_4.id,
    positional_args=[literal_8.id, literal_11.id],
)
