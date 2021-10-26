import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = []
y = [x]
x.append(10)
y[0].append(11)

lineapy.linea_publish(x, \'x\')
lineapy.linea_publish(y, \'y\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_list__",
    ).id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_list__",
    ).id,
    positional_args=[call_1.id],
)
mutate_1 = MutateNode(
    source_id=call_1.id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=0,
            end_lineno=4,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=0,
                end_lineno=4,
                end_col_offset=8,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                call_1.id,
                LiteralNode(
                    value="append",
                ).id,
            ],
        ).id,
        positional_args=[
            LiteralNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=9,
                    end_lineno=4,
                    end_col_offset=11,
                    source_code=source_1.id,
                ),
                value=10,
            ).id
        ],
    ).id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=4,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=2,
                end_lineno=5,
                end_col_offset=3,
                source_code=source_1.id,
            ),
            value=0,
        ).id,
    ],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=0,
            end_lineno=5,
            end_col_offset=11,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_5.id,
            LiteralNode(
                value="append",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=12,
                end_lineno=5,
                end_col_offset=14,
                source_code=source_1.id,
            ),
            value=11,
        ).id
    ],
)
mutate_2 = MutateNode(
    source_id=call_2.id,
    call_id=call_7.id,
)
mutate_3 = MutateNode(
    source_id=call_5.id,
    call_id=call_7.id,
)
