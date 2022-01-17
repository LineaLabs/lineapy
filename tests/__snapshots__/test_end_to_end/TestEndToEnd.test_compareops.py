import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""b = 1 < 2 < 3
assert b""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_assert",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=13,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="lt",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=4,
                        end_lineno=1,
                        end_col_offset=13,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="lt",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=4,
                                end_lineno=1,
                                end_col_offset=5,
                                source_code=source_1.id,
                            ),
                            value=1,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=8,
                                end_lineno=1,
                                end_col_offset=9,
                                source_code=source_1.id,
                            ),
                            value=2,
                        ).id,
                    ],
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=12,
                        end_lineno=1,
                        end_col_offset=13,
                        source_code=source_1.id,
                    ),
                    value=3,
                ).id,
            ],
        ).id
    ],
)
