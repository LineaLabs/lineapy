import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="getitem",
)
literal_1 = LiteralNode(
    value="sum",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="pandas",
)
literal_4 = LiteralNode(
    value="lineapy",
)
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="file_system",
)
lookup_5 = LookupNode(
    name="getattr",
)
lookup_6 = LookupNode(
    name="l_import",
)
literal_5 = LiteralNode(
    value="read_csv",
)
lookup_7 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import pandas as pd
import lineapy

df = pd.read_csv(\'tests/simple_data.csv\')
s = df[\'a\'].sum()

lineapy.save(s, "Graph With CSV Import")
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
    positional_args=[literal_3.id],
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
        col_offset=0,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[literal_4.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    name="lineapy",
    version="",
    package_name="lineapy",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_1.id, literal_5.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=17,
        end_lineno=4,
        end_col_offset=40,
        source_code=source_1.id,
    ),
    value="tests/simple_data.csv",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_6.id],
    implicit_dependencies=[lookup_4.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=7,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value="a",
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_4.id, literal_7.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_5.id, literal_1.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_2.id, literal_2.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=16,
        end_lineno=7,
        end_col_offset=39,
        source_code=source_1.id,
    ),
    value="Graph With CSV Import",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=40,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[call_7.id, literal_8.id],
)
