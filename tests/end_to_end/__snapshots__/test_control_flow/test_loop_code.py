import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_exec_statement",
)
literal_1 = LiteralNode(
    value="""for x in range(9):
    a.append(x)
    b += x""",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="lineapy",
)
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="l_list",
)
lookup_5 = LookupNode(
    name="add",
)
source_1 = SourceCode(
    code="""import lineapy
a = []
b = 0
for x in range(9):
    a.append(x)
    b += x
x = sum(a)
y = x + b

lineapy.save(y, \'y\')
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=0,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=6,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_1.id],
    global_reads={"a": call_2.id, "b": literal_4.id},
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_3.id,
)
global_1 = GlobalNode(
    name="b",
    call_id=call_3.id,
)
global_2 = GlobalNode(
    name="x",
    call_id=call_3.id,
)
lookup_6 = LookupNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="sum",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[mutate_1.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=4,
        end_lineno=8,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_4.id, global_1.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=16,
        end_lineno=10,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="y",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[call_5.id, literal_5.id],
)
