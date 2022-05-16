import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
b=30
def foo(a):
    return a - 10
c = foo(b)

lineapy.save(c, \'c\')
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
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=0,
            end_lineno=7,
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
        CallNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=4,
                end_lineno=5,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            function_id=GlobalNode(
                name="foo",
                call_id=CallNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=0,
                        end_lineno=4,
                        end_col_offset=17,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_exec_statement",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="""def foo(a):
    return a - 10""",
                        ).id
                    ],
                ).id,
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=2,
                        end_lineno=2,
                        end_col_offset=4,
                        source_code=source_1.id,
                    ),
                    value=30,
                ).id
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=16,
                end_lineno=7,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="c",
        ).id,
    ],
)
