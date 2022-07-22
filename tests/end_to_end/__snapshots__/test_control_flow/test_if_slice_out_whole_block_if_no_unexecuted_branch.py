import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="lt",
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
if a < 20:
    b = 20

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
        col_offset=7,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=20,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    test_id=call_2.id,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    value=20,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=16,
        end_lineno=6,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_3.id, literal_6.id],
)
