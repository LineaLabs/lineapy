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
lookup_4 = LookupNode(
    name="getitem",
)
literal_1 = LiteralNode(
    value="read_csv",
)
lookup_5 = LookupNode(
    name="l_list",
)
lookup_6 = LookupNode(
    name="l_tuple",
)
lookup_7 = LookupNode(
    name="file_system",
)
lookup_8 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="to_csv",
)
literal_3 = LiteralNode(
    value="lineapy",
)
literal_4 = LiteralNode(
    value="pandas",
)
lookup_9 = LookupNode(
    name="getattr",
)
literal_5 = LiteralNode(
    value="save",
)
literal_6 = LiteralNode(
    value="read_csv",
)
lookup_10 = LookupNode(
    name="getattr",
)
literal_7 = LiteralNode(
    value="DataFrame",
)
lookup_11 = LookupNode(
    name="getattr",
)
literal_8 = LiteralNode(
    value="to_csv",
)
lookup_12 = LookupNode(
    name="l_import",
)
lookup_13 = LookupNode(
    name="l_list",
)
lookup_14 = LookupNode(
    name="l_tuple",
)
lookup_15 = LookupNode(
    name="getattr",
)
lookup_16 = LookupNode(
    name="getitem",
)
lookup_17 = LookupNode(
    name="add",
)
lookup_18 = LookupNode(
    name="setitem",
)
source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_csv("test.csv", index=False)

df2 = pd.read_csv("test.csv")
df2["c"] = df2["a"] + df2["b"]
df2.to_csv("test2.csv", index=False)

df3 = pd.read_csv("test.csv")

lineapy.save(df3, \'df3\')
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_12.id,
    positional_args=[literal_4.id],
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
    positional_args=[call_2.id, literal_7.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=19,
        end_lineno=3,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    value="a",
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=25,
        end_lineno=3,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    value=1,
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=28,
        end_lineno=3,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value=2,
)
literal_12 = LiteralNode(
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
    function_id=lookup_5.id,
    positional_args=[literal_10.id, literal_11.id, literal_12.id],
)
call_5 = CallNode(
    function_id=lookup_6.id,
    positional_args=[literal_9.id, call_4.id],
)
literal_13 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=35,
        end_lineno=3,
        end_col_offset=38,
        source_code=source_1.id,
    ),
    value="b",
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=41,
        end_lineno=3,
        end_col_offset=42,
        source_code=source_1.id,
    ),
    value=4,
)
literal_15 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=44,
        end_lineno=3,
        end_col_offset=45,
        source_code=source_1.id,
    ),
    value=5,
)
literal_16 = LiteralNode(
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
    function_id=lookup_13.id,
    positional_args=[literal_14.id, literal_15.id, literal_16.id],
)
call_7 = CallNode(
    function_id=lookup_14.id,
    positional_args=[literal_13.id, call_6.id],
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
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_9.id, literal_2.id],
)
literal_17 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=10,
        end_lineno=4,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    value="test.csv",
)
literal_18 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=28,
        end_lineno=4,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    value=False,
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=call_10.id,
    positional_args=[literal_17.id],
    keyword_args={"index": literal_18.id},
)
mutate_1 = MutateNode(
    source_id=lookup_7.id,
    call_id=call_11.id,
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=6,
        end_lineno=6,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_2.id, literal_1.id],
)
literal_19 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=18,
        end_lineno=6,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    value="test.csv",
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=6,
        end_lineno=6,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=call_12.id,
    positional_args=[literal_19.id],
    implicit_dependencies=[mutate_1.id],
)
literal_20 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value="c",
)
literal_21 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=15,
        end_lineno=7,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value="a",
)
call_14 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=11,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_13.id, literal_21.id],
)
literal_22 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=26,
        end_lineno=7,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value="b",
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=22,
        end_lineno=7,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_16.id,
    positional_args=[call_13.id, literal_22.id],
)
call_16 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=11,
        end_lineno=7,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_17.id,
    positional_args=[call_14.id, call_15.id],
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=lookup_18.id,
    positional_args=[call_13.id, literal_20.id, call_16.id],
)
mutate_2 = MutateNode(
    source_id=call_15.id,
    call_id=call_17.id,
)
mutate_3 = MutateNode(
    source_id=call_14.id,
    call_id=call_17.id,
)
mutate_4 = MutateNode(
    source_id=call_13.id,
    call_id=call_17.id,
)
call_18 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_15.id,
    positional_args=[mutate_4.id, literal_8.id],
)
literal_23 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=11,
        end_lineno=8,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    value="test2.csv",
)
literal_24 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=30,
        end_lineno=8,
        end_col_offset=35,
        source_code=source_1.id,
    ),
    value=False,
)
call_19 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=36,
        source_code=source_1.id,
    ),
    function_id=call_18.id,
    positional_args=[literal_23.id],
    keyword_args={"index": literal_24.id},
)
mutate_5 = MutateNode(
    source_id=mutate_1.id,
    call_id=call_19.id,
)
call_20 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=6,
        end_lineno=10,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_11.id,
    positional_args=[call_2.id, literal_6.id],
)
literal_25 = LiteralNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=18,
        end_lineno=10,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    value="test.csv",
)
call_21 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=6,
        end_lineno=10,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=call_20.id,
    positional_args=[literal_25.id],
    implicit_dependencies=[mutate_5.id],
)
call_22 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[call_1.id, literal_5.id],
)
literal_26 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=18,
        end_lineno=12,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value="df3",
)
call_23 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=call_22.id,
    positional_args=[call_21.id, literal_26.id],
)
