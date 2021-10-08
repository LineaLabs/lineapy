import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="a = [1]; del a[0]",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=9,
        end_lineno=1,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="delitem",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=7,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="__build_list__",
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
                ).id
            ],
            keyword_args={},
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=15,
                end_lineno=1,
                end_col_offset=16,
                source_code=source_1.id,
            ),
            value=0,
        ).id,
    ],
    keyword_args={},
)
