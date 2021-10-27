import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="a = [1]; del a[0]",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=5,
                end_lineno=1,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            value=1,
        ).id
    ],
)
mutate_1 = MutateNode(
    source_id=call_1.id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=9,
            end_lineno=1,
            end_col_offset=17,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="delitem",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=15,
                    end_lineno=1,
                    end_col_offset=16,
                    source_code=source_1.id,
                ),
                value=0,
            ).id,
        ],
    ).id,
)
