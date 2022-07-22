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
    value="data_transformers",
)
literal_2 = LiteralNode(
    value="altair",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="enable",
)
source_1 = SourceCode(
    code="import altair; altair.data_transformers.enable('json')",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    name="altair",
    version="",
    package_name="altair",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=15,
        end_lineno=1,
        end_col_offset=39,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_1.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=15,
        end_lineno=1,
        end_col_offset=46,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_2.id, literal_3.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=47,
        end_lineno=1,
        end_col_offset=53,
        source_code=source_1.id,
    ),
    value="json",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=15,
        end_lineno=1,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_4.id],
)
