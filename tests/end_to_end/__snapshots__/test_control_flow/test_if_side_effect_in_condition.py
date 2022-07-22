import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_list",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="save",
)
literal_2 = LiteralNode(
    value="lineapy",
)
literal_3 = LiteralNode(
    value="pop",
)
lookup_4 = LookupNode(
    name="l_alias",
)
lookup_5 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
a = [1, 2, 3]
if b := a.pop():
    b += 1

lineapy.save(a, \'a\')
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
    positional_args=[literal_2.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=1,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=8,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=2,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=11,
        end_lineno=2,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    value=3,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_4.id, literal_5.id, literal_6.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=8,
        end_lineno=3,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_2.id, literal_3.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=8,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_4.id],
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    test_id=call_5.id,
)
lookup_6 = LookupNode(
    control_dependency=if_1.id,
    name="l_exec_statement",
)
literal_7 = LiteralNode(
    control_dependency=if_1.id,
    value="b += 1",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    function_id=lookup_6.id,
    positional_args=[literal_7.id],
    global_reads={"b": call_5.id},
)
global_1 = GlobalNode(
    control_dependency=if_1.id,
    name="b",
    call_id=call_6.id,
)
call_7 = CallNode(
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
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=16,
        end_lineno=6,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_7.id,
    positional_args=[mutate_1.id, literal_8.id],
)
