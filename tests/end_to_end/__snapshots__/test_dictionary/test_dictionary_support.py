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
lookup_3 = LookupNode(
    name="getitem",
)
literal_1 = LiteralNode(
    value="sum",
)
literal_2 = LiteralNode(
    value="pandas",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="DataFrame",
)
lookup_5 = LookupNode(
    name="l_dict",
)
lookup_6 = LookupNode(
    name="l_tuple",
)
lookup_7 = LookupNode(
    name="l_list",
)
source_1 = SourceCode(
    code="""import pandas as pd
df = pd.DataFrame({"id": [1,2]})
x = df["id"].sum()
""",
    location=PosixPath("[source file path]"),
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
    positional_args=[literal_2.id],
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=19,
        end_lineno=2,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value="id",
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=26,
        end_lineno=2,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    value=1,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=28,
        end_lineno=2,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value=2,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=25,
        end_lineno=2,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_5.id, literal_6.id],
)
call_4 = CallNode(
    function_id=lookup_6.id,
    positional_args=[literal_4.id, call_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=18,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_4.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    function_id=call_2.id,
    positional_args=[call_5.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=7,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value="id",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_6.id, literal_7.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_7.id, literal_1.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
)
