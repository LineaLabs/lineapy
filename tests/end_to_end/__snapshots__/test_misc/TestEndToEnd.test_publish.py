import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="lineapy",
)
literal_2 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
a = abs(11)
lineapy.save(a, \'testing artifact publish\')
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
lookup_3 = LookupNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="abs",
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=8,
        end_lineno=2,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=11,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_3.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=16,
        end_lineno=3,
        end_col_offset=42,
        source_code=source_1.id,
    ),
    value="testing artifact publish",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[call_2.id, literal_4.id],
)
