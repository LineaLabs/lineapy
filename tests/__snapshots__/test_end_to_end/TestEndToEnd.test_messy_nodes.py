import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

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

lineapy.save(f, \'f\')
""",
    location=PosixPath("[source file path]"),
)
literal_2 = LiteralNode(
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
        literal_2.id,
    ],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=2,
        source_code=source_1.id,
    ),
    value=10,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=12,
            col_offset=0,
            end_lineno=12,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
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
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
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
                        literal_2.id,
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
                                literal_2.id,
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
                        ).id,
                    ],
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
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=12,
                col_offset=16,
                end_lineno=12,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="f",
        ).id,
    ],
)
