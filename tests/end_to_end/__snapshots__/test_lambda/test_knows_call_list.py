import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = 10
fn = lambda: a
def sum_call_list(xs):
    r = 0
    for x in xs:
        r += x()
    return r
r = sum_call_list([fn, fn])

lineapy.save(r, \'r\')
""",
    location=PosixPath("[source file path]"),
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=11,
            col_offset=0,
            end_lineno=11,
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
                lineno=9,
                col_offset=4,
                end_lineno=9,
                end_col_offset=27,
                source_code=source_1.id,
            ),
            function_id=GlobalNode(
                name="sum_call_list",
                call_id=CallNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=0,
                        end_lineno=8,
                        end_col_offset=12,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_exec_statement",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="""def sum_call_list(xs):
    r = 0
    for x in xs:
        r += x()
    return r""",
                        ).id
                    ],
                ).id,
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=9,
                        col_offset=18,
                        end_lineno=9,
                        end_col_offset=26,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_list",
                    ).id,
                    positional_args=[
                        CallNode(
                            source_location=SourceLocation(
                                lineno=3,
                                col_offset=5,
                                end_lineno=3,
                                end_col_offset=14,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="l_exec_expr",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="lambda: a",
                                ).id
                            ],
                        ).id,
                        CallNode(
                            source_location=SourceLocation(
                                lineno=3,
                                col_offset=5,
                                end_lineno=3,
                                end_col_offset=14,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="l_exec_expr",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="lambda: a",
                                ).id
                            ],
                        ).id,
                    ],
                ).id
            ],
            global_reads={
                "a": LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=4,
                        end_lineno=2,
                        end_col_offset=6,
                        source_code=source_1.id,
                    ),
                    value=10,
                ).id
            },
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=11,
                col_offset=16,
                end_lineno=11,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="r",
        ).id,
    ],
)
