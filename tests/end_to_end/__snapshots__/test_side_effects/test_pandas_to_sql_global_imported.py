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
    name="l_dict",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="connect",
)
literal_2 = LiteralNode(
    value="DataFrame",
)
literal_3 = LiteralNode(
    value="db",
)
lookup_5 = LookupNode(
    name="l_tuple",
)
lookup_6 = LookupNode(
    name="getattr",
)
literal_4 = LiteralNode(
    value="to_sql",
)
literal_5 = LiteralNode(
    value="sqlite3",
)
lookup_7 = LookupNode(
    name="l_list",
)
literal_6 = LiteralNode(
    value="lineapy",
)
lookup_8 = LookupNode(
    name="getattr",
)
lookup_9 = LookupNode(
    name="l_import",
)
lookup_10 = LookupNode(
    name="l_tuple",
)
literal_7 = LiteralNode(
    value="save",
)
literal_8 = LiteralNode(
    value="pandas",
)
lookup_11 = LookupNode(
    name="l_list",
)
lookup_12 = LookupNode(
    name="l_import",
)
lookup_13 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""from lineapy import save, db
import pandas as pd
import sqlite3

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
conn = sqlite3.connect(\':memory:\')
df.to_sql(name="test", con=conn,index=False)

save(db, "db")
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=28,
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
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_6.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_7.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_1.id, literal_3.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_12.id,
    positional_args=[literal_8.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    name="pandas",
    version="",
    package_name="pandas",
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    name="sqlite3",
    version="",
    package_name="sqlite3",
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[literal_5.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_4.id, literal_2.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=19,
        end_lineno=5,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    value="a",
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=25,
        end_lineno=5,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    value=1,
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=28,
        end_lineno=5,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value=2,
)
literal_12 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=31,
        end_lineno=5,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    value=3,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=24,
        end_lineno=5,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    function_id=lookup_11.id,
    positional_args=[literal_10.id, literal_11.id, literal_12.id],
)
call_8 = CallNode(
    function_id=lookup_10.id,
    positional_args=[literal_9.id, call_7.id],
)
literal_13 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=35,
        end_lineno=5,
        end_col_offset=38,
        source_code=source_1.id,
    ),
    value="b",
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=41,
        end_lineno=5,
        end_col_offset=42,
        source_code=source_1.id,
    ),
    value=4,
)
literal_15 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=44,
        end_lineno=5,
        end_col_offset=45,
        source_code=source_1.id,
    ),
    value=5,
)
literal_16 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=47,
        end_lineno=5,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    value=6,
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=40,
        end_lineno=5,
        end_col_offset=49,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_14.id, literal_15.id, literal_16.id],
)
call_10 = CallNode(
    function_id=lookup_5.id,
    positional_args=[literal_13.id, call_9.id],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=18,
        end_lineno=5,
        end_col_offset=50,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_8.id, call_10.id],
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=51,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[call_11.id],
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=7,
        end_lineno=6,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_5.id, literal_1.id],
)
literal_17 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=23,
        end_lineno=6,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    value=":memory:",
)
call_14 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=7,
        end_lineno=6,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=call_13.id,
    positional_args=[literal_17.id],
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_13.id,
    positional_args=[call_12.id, literal_4.id],
)
literal_18 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=15,
        end_lineno=7,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    value="test",
)
literal_19 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=38,
        end_lineno=7,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    value=False,
)
call_16 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=44,
        source_code=source_1.id,
    ),
    function_id=call_15.id,
    keyword_args={"con": call_14.id, "index": literal_19.id, "name": literal_18.id},
)
mutate_1 = MutateNode(
    source_id=call_3.id,
    call_id=call_16.id,
)
literal_20 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=9,
        end_lineno=9,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value="db",
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=call_2.id,
    positional_args=[mutate_1.id, literal_20.id],
)
