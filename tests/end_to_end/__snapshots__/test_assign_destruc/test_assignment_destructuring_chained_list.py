import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""x=[1,2]
c = x
a = b = c""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_alias",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=2,
                end_lineno=1,
                end_col_offset=7,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=3,
                        end_lineno=1,
                        end_col_offset=4,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=5,
                        end_lineno=1,
                        end_col_offset=6,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id
    ],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_alias",
    ).id,
    positional_args=[call_2.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_alias",
    ).id,
    positional_args=[call_2.id],
)
