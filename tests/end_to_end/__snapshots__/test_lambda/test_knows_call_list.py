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

lineapy.linea_publish(r, \'r\')
""",
    location=PosixPath("[source file path]"),
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=4,
        end_lineno=9,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getitem",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=0,
                    end_lineno=8,
                    end_col_offset=12,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="__exec__",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""def sum_call_list(xs):
    r = 0
    for x in xs:
        r += x()
    return r""",
                    ).id,
                    LiteralNode(
                        value=False,
                    ).id,
                    LiteralNode(
                        value="sum_call_list",
                    ).id,
                ],
            ).id,
            LiteralNode(
                value=0,
            ).id,
        ],
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
                name="__build_list__",
            ).id,
            positional_args=[
                CallNode(
                    function_id=LookupNode(
                        name="getitem",
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
                                name="__exec__",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="lambda: a",
                                ).id,
                                LiteralNode(
                                    value=True,
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            value=0,
                        ).id,
                    ],
                ).id,
                CallNode(
                    function_id=LookupNode(
                        name="getitem",
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
                                name="__exec__",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="lambda: a",
                                ).id,
                                LiteralNode(
                                    value=True,
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            value=0,
                        ).id,
                    ],
                ).id,
            ],
        ).id
    ],
)
