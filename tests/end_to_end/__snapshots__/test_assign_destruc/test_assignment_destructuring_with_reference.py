import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""a = [1,2,5]
b, c, d = a""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_unpack_sequence",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
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
                        col_offset=5,
                        end_lineno=1,
                        end_col_offset=6,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=7,
                        end_lineno=1,
                        end_col_offset=8,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=9,
                        end_lineno=1,
                        end_col_offset=10,
                        source_code=source_1.id,
                    ),
                    value=5,
                ).id,
            ],
        ).id,
        LiteralNode(
            value=3,
        ).id,
    ],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            value=1,
        ).id,
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            value=0,
        ).id,
    ],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            value=2,
        ).id,
    ],
)
