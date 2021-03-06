import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""c = [[1, 2], 3]
[a, b], *rest = c""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_unpack_ex",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=5,
                        end_lineno=1,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_list",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=6,
                                end_lineno=1,
                                end_col_offset=7,
                                source_code=source_1.id,
                            ),
                            value=1,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=9,
                                end_lineno=1,
                                end_col_offset=10,
                                source_code=source_1.id,
                            ),
                            value=2,
                        ).id,
                    ],
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=13,
                        end_lineno=1,
                        end_col_offset=14,
                        source_code=source_1.id,
                    ),
                    value=3,
                ).id,
            ],
        ).id,
        LiteralNode(
            value=1,
        ).id,
        LiteralNode(
            value=0,
        ).id,
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_3.id,
        LiteralNode(
            value=1,
        ).id,
    ],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_unpack_sequence",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=0,
                end_lineno=2,
                end_col_offset=17,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getitem",
            ).id,
            positional_args=[
                call_3.id,
                LiteralNode(
                    value=0,
                ).id,
            ],
        ).id,
        LiteralNode(
            value=2,
        ).id,
    ],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_6.id,
        LiteralNode(
            value=1,
        ).id,
    ],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_6.id,
        LiteralNode(
            value=0,
        ).id,
    ],
)
