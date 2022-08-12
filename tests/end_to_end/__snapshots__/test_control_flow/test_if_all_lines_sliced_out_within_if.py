import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = 10
if a < 20:
    b = 10
else:
    a += 20

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
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    companion_id=else_1.id,
    test_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=3,
            end_lineno=3,
            end_col_offset=9,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="lt",
        ).id,
        positional_args=[
            literal_3.id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=7,
                    end_lineno=3,
                    end_col_offset=9,
                    source_code=source_1.id,
                ),
                value=20,
            ).id,
        ],
    ).id,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    value=10,
)
else_1 = ElseNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=4,
        source_code=source_1.id,
    ),
    companion_id=if_1.id,
)
unexec_1 = UnexecNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    control_dependency=else_1.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    control_dependency=unexec_1.id,
    function_id=LookupNode(
        control_dependency=unexec_1.id,
        name="l_exec_statement",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=4,
                end_lineno=6,
                end_col_offset=11,
                source_code=source_1.id,
            ),
            control_dependency=unexec_1.id,
            value="a += 20",
        ).id
    ],
)
call_5 = CallNode(
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
        literal_3.id,
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
