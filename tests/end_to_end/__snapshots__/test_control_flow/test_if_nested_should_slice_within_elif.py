import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = 10
b = 20
if a <= 2:
    a = 1
    b = 2
elif a > 0:
    a = 3
    b = 4
else:
    a = 5
    b = 6

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
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=20,
)
else_1 = ElseNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=0,
        source_code=source_1.id,
    ),
    companion_id=IfNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=3,
            end_lineno=4,
            end_col_offset=9,
            source_code=source_1.id,
        ),
        companion_id=else_1.id,
        unexec_id=LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=4,
                end_lineno=6,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            value="""a = 1
b = 2""",
        ).id,
        test_id=CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=3,
                end_lineno=4,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="le",
            ).id,
            positional_args=[
                literal_3.id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=8,
                        end_lineno=4,
                        end_col_offset=9,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id,
    ).id,
)
if_2 = IfNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=5,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
    companion_id=else_2.id,
    test_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=5,
            end_lineno=7,
            end_col_offset=10,
            source_code=source_1.id,
        ),
        control_dependency=else_1.id,
        function_id=LookupNode(
            control_dependency=else_1.id,
            name="gt",
        ).id,
        positional_args=[
            literal_3.id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=7,
                    col_offset=9,
                    end_lineno=7,
                    end_col_offset=10,
                    source_code=source_1.id,
                ),
                control_dependency=else_1.id,
                value=0,
            ).id,
        ],
    ).id,
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=8,
        end_lineno=9,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    control_dependency=if_2.id,
    value=4,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=14,
        col_offset=0,
        end_lineno=14,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=14,
            col_offset=0,
            end_lineno=14,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_import",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="lineapy",
                    ).id
                ],
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=8,
                col_offset=8,
                end_lineno=8,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            control_dependency=if_2.id,
            value=3,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=14,
                col_offset=16,
                end_lineno=14,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
    ],
)
