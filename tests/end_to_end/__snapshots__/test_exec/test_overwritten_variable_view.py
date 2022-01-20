import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = []
y = [x]
if True:
    x = [x]
x.append(1)
y.append(2)

lineapy.save(x, \'x\')
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
    library=Library(
        name="lineapy",
    ),
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
        name="l_list",
    ).id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_exec_statement",
    ).id,
    positional_args=[
        LiteralNode(
            value="""if True:
    x = [x]""",
        ).id
    ],
    global_reads={"x": call_1.id},
)
global_1 = GlobalNode(
    name="x",
    call_id=call_3.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=6,
            col_offset=0,
            end_lineno=6,
            end_col_offset=8,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            global_1.id,
            LiteralNode(
                value="append",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=9,
                end_lineno=6,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=1,
        ).id
    ],
)
mutate_3 = MutateNode(
    source_id=MutateNode(
        source_id=CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=4,
                end_lineno=3,
                end_col_offset=7,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[call_1.id],
        ).id,
        call_id=call_3.id,
    ).id,
    call_id=call_5.id,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=0,
            end_lineno=7,
            end_col_offset=8,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            mutate_3.id,
            LiteralNode(
                value="append",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=9,
                end_lineno=7,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=2,
        ).id
    ],
)
mutate_9 = MutateNode(
    source_id=MutateNode(
        source_id=MutateNode(
            source_id=call_1.id,
            call_id=call_3.id,
        ).id,
        call_id=call_5.id,
    ).id,
    call_id=call_7.id,
)
mutate_10 = MutateNode(
    source_id=MutateNode(
        source_id=call_3.id,
        call_id=call_5.id,
    ).id,
    call_id=call_7.id,
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=9,
            col_offset=0,
            end_lineno=9,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        MutateNode(
            source_id=MutateNode(
                source_id=global_1.id,
                call_id=call_5.id,
            ).id,
            call_id=call_7.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=16,
                end_lineno=9,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="x",
        ).id,
    ],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=10,
            col_offset=0,
            end_lineno=10,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        MutateNode(
            source_id=mutate_3.id,
            call_id=call_7.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=10,
                col_offset=16,
                end_lineno=10,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="y",
        ).id,
    ],
)
