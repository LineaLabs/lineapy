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
    name="setitem",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="setitem",
)
literal_1 = LiteralNode(
    value="lineapy",
)
lookup_6 = LookupNode(
    name="l_dict",
)
literal_2 = LiteralNode(
    value="save",
)
lookup_7 = LookupNode(
    name="getattr",
)
lookup_8 = LookupNode(
    name="l_dict",
)
lookup_9 = LookupNode(
    name="setitem",
)
literal_3 = LiteralNode(
    value="save",
)
lookup_10 = LookupNode(
    name="getattr",
)
literal_4 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
x = {}
y = {}
z = {}
x[\'y\'] = y
y[\'z\'] = z
z[\'a\'] = 1

lineapy.save(x, \'x\')
lineapy.save(y, \'y\')
lineapy.save(z, \'z\')
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
    positional_args=[literal_1.id],
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
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=2,
        end_lineno=5,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value="y",
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_2.id, literal_5.id, call_3.id],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_5.id,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=2,
        end_lineno=6,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value="z",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[call_3.id, literal_6.id, call_4.id],
)
mutate_2 = MutateNode(
    source_id=call_3.id,
    call_id=call_6.id,
)
mutate_3 = MutateNode(
    source_id=mutate_1.id,
    call_id=call_6.id,
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=2,
        end_lineno=7,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value="a",
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=9,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=1,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_4.id, literal_7.id, literal_8.id],
)
mutate_4 = MutateNode(
    source_id=call_4.id,
    call_id=call_7.id,
)
mutate_5 = MutateNode(
    source_id=mutate_3.id,
    call_id=call_7.id,
)
mutate_6 = MutateNode(
    source_id=mutate_2.id,
    call_id=call_7.id,
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_4.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=16,
        end_lineno=9,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[mutate_5.id, literal_9.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_10.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=16,
        end_lineno=10,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="y",
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_10.id,
    positional_args=[mutate_6.id, literal_10.id],
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=16,
        end_lineno=11,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="z",
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_12.id,
    positional_args=[mutate_4.id, literal_11.id],
)
