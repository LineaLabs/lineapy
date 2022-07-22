import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_dict",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="save",
)
lookup_4 = LookupNode(
    name="l_list",
)
lookup_5 = LookupNode(
    name="l_tuple",
)
lookup_6 = LookupNode(
    name="setitem",
)
lookup_7 = LookupNode(
    name="add",
)
lookup_8 = LookupNode(
    name="getitem",
)
literal_2 = LiteralNode(
    value="lineapy",
)
literal_3 = LiteralNode(
    value="pandas",
)
lookup_9 = LookupNode(
    name="getitem",
)
lookup_10 = LookupNode(
    name="getattr",
)
literal_4 = LiteralNode(
    value="DataFrame",
)
lookup_11 = LookupNode(
    name="l_import",
)
lookup_12 = LookupNode(
    name="l_list",
)
lookup_13 = LookupNode(
    name="l_tuple",
)
source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
df["C"] = df["A"] + df["B"]

lineapy.save(df, \'df\')
""",
    location=PosixPath("[source file path]"),
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_11.id,
    positional_args=[literal_3.id],
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
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=5,
        end_lineno=3,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_10.id,
    positional_args=[call_2.id, literal_4.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=19,
        end_lineno=3,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    value="A",
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=25,
        end_lineno=3,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    value=1,
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=28,
        end_lineno=3,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value=2,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=31,
        end_lineno=3,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    value=3,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=24,
        end_lineno=3,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_6.id, literal_7.id, literal_8.id],
)
call_5 = CallNode(
    function_id=lookup_5.id,
    positional_args=[literal_5.id, call_4.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=35,
        end_lineno=3,
        end_col_offset=38,
        source_code=source_1.id,
    ),
    value="B",
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=41,
        end_lineno=3,
        end_col_offset=42,
        source_code=source_1.id,
    ),
    value=4,
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=44,
        end_lineno=3,
        end_col_offset=45,
        source_code=source_1.id,
    ),
    value=5,
)
literal_12 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=47,
        end_lineno=3,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    value=6,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=40,
        end_lineno=3,
        end_col_offset=49,
        source_code=source_1.id,
    ),
    function_id=lookup_12.id,
    positional_args=[literal_10.id, literal_11.id, literal_12.id],
)
call_7 = CallNode(
    function_id=lookup_13.id,
    positional_args=[literal_9.id, call_6.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=18,
        end_lineno=3,
        end_col_offset=50,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_5.id, call_7.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=5,
        end_lineno=3,
        end_col_offset=51,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[call_8.id],
)
literal_13 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=3,
        end_lineno=4,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value="C",
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=13,
        end_lineno=4,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    value="A",
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=10,
        end_lineno=4,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[call_9.id, literal_14.id],
)
literal_15 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=23,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    value="B",
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=20,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_9.id, literal_15.id],
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=10,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_10.id, call_11.id],
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_9.id, literal_13.id, call_12.id],
)
mutate_1 = MutateNode(
    source_id=call_9.id,
    call_id=call_13.id,
)
mutate_2 = MutateNode(
    source_id=call_11.id,
    call_id=call_13.id,
)
mutate_3 = MutateNode(
    source_id=call_10.id,
    call_id=call_13.id,
)
call_14 = CallNode(
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
literal_16 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=17,
        end_lineno=6,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    value="df",
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=call_14.id,
    positional_args=[mutate_1.id, literal_16.id],
)
