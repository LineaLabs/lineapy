import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="a = '{{ {0} }}'.format('foo')",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            value="{{ {0} }}",
        ).id,
        LiteralNode(
            value="format",
        ).id,
    ],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_1.id,
)
global_2 = GlobalNode(
    name="c",
    call_id=call_1.id,
)
global_3 = GlobalNode(
    name="b",
    call_id=call_1.id,
)
global_4 = GlobalNode(
    name="new_df",
    call_id=call_1.id,
)
global_5 = GlobalNode(
    name="my_function",
    call_id=call_1.id,
)
global_6 = GlobalNode(
    name="v",
    call_id=call_1.id,
)
global_7 = GlobalNode(
    name="df",
    call_id=call_1.id,
)
global_8 = GlobalNode(
    name="DataFrame",
    call_id=call_1.id,
)
global_9 = GlobalNode(
    name="pandas",
    call_id=call_1.id,
)
global_10 = GlobalNode(
    name="bs",
    call_id=call_1.id,
)
global_11 = GlobalNode(
    name="math",
    call_id=call_1.id,
)
global_12 = GlobalNode(
    name="a",
    call_id=call_1.id,
)
global_13 = GlobalNode(
    name="x",
    call_id=call_1.id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=call_1.id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=23,
                end_lineno=1,
                end_col_offset=28,
                source_code=source_1.id,
            ),
            value="foo",
        ).id
    ],
)
