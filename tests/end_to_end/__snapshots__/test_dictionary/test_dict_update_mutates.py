import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_tuple",
)
lookup_3 = LookupNode(
    name="l_tuple",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="lineapy",
)
lookup_5 = LookupNode(
    name="l_tuple",
)
lookup_6 = LookupNode(
    name="l_dict",
)
lookup_7 = LookupNode(
    name="l_dict",
)
lookup_8 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="update",
)
source_1 = SourceCode(
    code="""import lineapy
x = {\'a\': 1, \'b\': 2}
x.update({\'a\': 3})

lineapy.save(x, \'x\')
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
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value="a",
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=10,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value=1,
)
call_2 = CallNode(
    function_id=lookup_2.id,
    positional_args=[literal_4.id, literal_5.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=13,
        end_lineno=2,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    value="b",
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=18,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value=2,
)
call_3 = CallNode(
    function_id=lookup_5.id,
    positional_args=[literal_6.id, literal_7.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_2.id, call_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_4.id, literal_3.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=10,
        end_lineno=3,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value="a",
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=15,
        end_lineno=3,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    value=3,
)
call_6 = CallNode(
    function_id=lookup_3.id,
    positional_args=[literal_8.id, literal_9.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=9,
        end_lineno=3,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_6.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[call_7.id],
)
mutate_1 = MutateNode(
    source_id=call_4.id,
    call_id=call_8.id,
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=16,
        end_lineno=5,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_9.id,
    positional_args=[mutate_1.id, literal_10.id],
)
