import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = {}
y = {}
z = {}
x[\'y\'] = y
y[\'z\'] = z
z[\'a\'] = 1

lineapy.linea_publish(x, \'x\')
lineapy.linea_publish(y, \'y\')
lineapy.linea_publish(z, \'z\')
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
        name="__build_dict__",
    ).id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_dict__",
    ).id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_dict__",
    ).id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setitem",
    ).id,
    positional_args=[
        call_1.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=2,
                end_lineno=5,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value="y",
        ).id,
        call_2.id,
    ],
)
mutate_2 = MutateNode(
    source_id=call_2.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setitem",
    ).id,
    positional_args=[
        mutate_2.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=2,
                end_lineno=6,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value="z",
        ).id,
        call_3.id,
    ],
)
mutate_3 = MutateNode(
    source_id=call_3.id,
    call_id=call_5.id,
)
mutate_5 = MutateNode(
    source_id=MutateNode(
        source_id=call_1.id,
        call_id=call_4.id,
    ).id,
    call_id=call_5.id,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setitem",
    ).id,
    positional_args=[
        mutate_3.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=2,
                end_lineno=7,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=9,
                end_lineno=7,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
    ],
)
mutate_8 = MutateNode(
    source_id=mutate_5.id,
    call_id=call_6.id,
)
mutate_11 = MutateNode(
    source_id=MutateNode(
        source_id=MutateNode(
            source_id=mutate_2.id,
            call_id=call_5.id,
        ).id,
        call_id=call_6.id,
    ).id,
    call_id=call_6.id,
)
mutate_12 = MutateNode(
    source_id=mutate_5.id,
    call_id=call_6.id,
)
mutate_13 = MutateNode(
    source_id=MutateNode(
        source_id=MutateNode(
            source_id=mutate_2.id,
            call_id=call_5.id,
        ).id,
        call_id=call_6.id,
    ).id,
    call_id=call_6.id,
)
mutate_14 = MutateNode(
    source_id=mutate_3.id,
    call_id=call_6.id,
)
mutate_16 = MutateNode(
    source_id=mutate_3.id,
    call_id=call_6.id,
)
mutate_17 = MutateNode(
    source_id=MutateNode(
        source_id=MutateNode(
            source_id=mutate_5.id,
            call_id=call_5.id,
        ).id,
        call_id=call_6.id,
    ).id,
    call_id=call_6.id,
)
