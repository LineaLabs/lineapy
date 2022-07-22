import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_list",
)
lookup_2 = LookupNode(
    name="gt",
)
source_1 = SourceCode(
    code="""bs = [1,2]
if len(bs) > 4:
    pass
else:
    bs.append(3)
""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=6,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=1,
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=8,
        end_lineno=1,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=2,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=5,
        end_lineno=1,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id, literal_2.id],
)
lookup_3 = LookupNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=3,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    name="len",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=3,
        end_lineno=2,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=13,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    value=4,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=3,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_3.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value="pass",
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=3,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    companion_id=else_1.id,
    unexec_id=literal_4.id,
    test_id=call_3.id,
)
else_1 = ElseNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=4,
        source_code=source_1.id,
    ),
    companion_id=if_1.id,
)
lookup_4 = LookupNode(
    control_dependency=else_1.id,
    name="getattr",
)
literal_5 = LiteralNode(
    control_dependency=else_1.id,
    value="append",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_5.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=14,
        end_lineno=5,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
    value=3,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
    function_id=call_4.id,
    positional_args=[literal_6.id],
)
mutate_1 = MutateNode(
    control_dependency=else_1.id,
    source_id=call_1.id,
    call_id=call_5.id,
)
