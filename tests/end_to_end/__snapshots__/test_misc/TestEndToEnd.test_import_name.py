import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="eq",
)
lookup_3 = LookupNode(
    name="l_assert",
)
literal_1 = LiteralNode(
    value="pandas",
)
literal_2 = LiteralNode(
    value="__name__",
)
lookup_4 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import pandas as pd
assert pd.__name__ == \'pandas\'""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    name="pandas",
    version="",
    package_name="pandas",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=7,
        end_lineno=2,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=22,
        end_lineno=2,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    value="pandas",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=7,
        end_lineno=2,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_3.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_3.id],
)
