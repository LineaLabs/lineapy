import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="setitem",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="lineapy",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="l_dict",
)
literal_4 = LiteralNode(
    value="save",
)
lookup_6 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
x = {}
before = str(x)
x[\'a\'] = 1
after = str(x)

lineapy.save(x, \'x\')
lineapy.save(before, \'before\')
lineapy.save(after, \'after\')
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
    function_id=lookup_5.id,
)
lookup_7 = LookupNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=9,
        end_lineno=3,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    name="str",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=9,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_2.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=2,
        end_lineno=4,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value="a",
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=9,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=1,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_5.id, literal_6.id],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_4.id,
)
lookup_8 = LookupNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=8,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    name="str",
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=8,
        end_lineno=5,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[mutate_1.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=16,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[mutate_1.id, literal_7.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=21,
        end_lineno=8,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    value="before",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[call_3.id, literal_8.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_1.id, literal_4.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=20,
        end_lineno=9,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    value="after",
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=call_10.id,
    positional_args=[call_5.id, literal_9.id],
)
