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
lookup_2 = LookupNode(
    name="l_alias",
)
literal_2 = LiteralNode(
    value="save",
)
lookup_3 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
x = 100
y = x
x = 200
lineapy.save(y, "y")
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
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=100,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=200,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=16,
        end_lineno=5,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="y",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[call_2.id, literal_5.id],
)
