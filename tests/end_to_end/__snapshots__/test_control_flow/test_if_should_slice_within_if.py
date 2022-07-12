import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = 10
b = 20
if a > 5:
    a = 5
    b = 6

lineapy.save(a, \'a\')
lineapy.save(b, \'b\')
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
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="lineapy",
        ).id
    ],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=20,
)
if_else_1 = IfElseNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=3,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    test_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=3,
            end_lineno=4,
            end_col_offset=8,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="gt",
        ).id,
        positional_args=[
            LiteralNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=4,
                    end_lineno=2,
                    end_col_offset=6,
                    source_code=source_1.id,
                ),
                value=10,
            ).id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=7,
                    end_lineno=4,
                    end_col_offset=8,
                    source_code=source_1.id,
                ),
                value=5,
            ).id,
        ],
    ).id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=8,
            col_offset=0,
            end_lineno=8,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=8,
                end_lineno=5,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            control_dependency=if_else_1.id,
            value=5,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=8,
                col_offset=16,
                end_lineno=8,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
    ],
)
call_6 = CallNode(
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
            call_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=8,
                end_lineno=6,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            control_dependency=if_else_1.id,
            value=6,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=16,
                end_lineno=9,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="b",
        ).id,
    ],
)
