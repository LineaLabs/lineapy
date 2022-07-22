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
    code="""from lineapy import save
a = 1
save(a, \'another_import_method\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    name="lineapy",
    version="",
    package_name="lineapy",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_2.id],
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
        end_col_offset=31,
        source_code=source_1.id,
    ),
    value="another_import_method",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    function_id=call_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
