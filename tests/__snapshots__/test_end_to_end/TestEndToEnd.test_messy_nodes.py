import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = 1
b = a + 2
c = 2
d = 4
e = d + a
f = a * b * c
10
e
g = e

lineapy.linea_publish(f, \'f\')
""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=1,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="add",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=4,
                end_lineno=5,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=4,
        ).id,
        literal_1.id,
    ],
    global_reads={},
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="mul",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=4,
                end_lineno=7,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="mul",
            ).id,
            positional_args=[
                literal_1.id,
                CallNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=4,
                        end_lineno=3,
                        end_col_offset=9,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="add",
                    ).id,
                    positional_args=[
                        literal_1.id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=3,
                                col_offset=8,
                                end_lineno=3,
                                end_col_offset=9,
                                source_code=source_1.id,
                            ),
                            value=2,
                        ).id,
                    ],
                    global_reads={},
                ).id,
            ],
            global_reads={},
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=4,
                end_lineno=4,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=2,
        ).id,
    ],
    global_reads={},
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=2,
        source_code=source_1.id,
    ),
    value=10,
)
