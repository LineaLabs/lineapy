import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
def foo():
    def inner():
        return a
    return inner
a = 10
c = foo()()

lineapy.save(c, \'c\')
""",
    location=PosixPath("[source file path]"),
)
call_5 = CallNode(
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
            ImportNode(
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
                end_col_offset=11,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                source_location=SourceLocation(
                    lineno=7,
                    col_offset=4,
                    end_lineno=7,
                    end_col_offset=9,
                    source_code=source_1.id,
                ),
                function_id=GlobalNode(
                    name="foo",
                    call_id=CallNode(
                        source_location=SourceLocation(
                            lineno=2,
                            col_offset=0,
                            end_lineno=5,
                            end_col_offset=16,
                            source_code=source_1.id,
                        ),
                        function_id=LookupNode(
                            name="l_exec_statement",
                        ).id,
                        positional_args=[
                            LiteralNode(
                                value="""def foo():
    def inner():
        return a
    return inner""",
                            ).id
                        ],
                    ).id,
                ).id,
            ).id,
            global_reads={
                "a": LiteralNode(
                    source_location=SourceLocation(
                        lineno=6,
                        col_offset=4,
                        end_lineno=6,
                        end_col_offset=6,
                        source_code=source_1.id,
                    ),
                    value=10,
                ).id
            },
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=16,
                end_lineno=9,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="c",
        ).id,
    ],
)
