import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = abs(11)
b = min(a, 10)
print(b)
""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=0,
            end_lineno=3,
            end_col_offset=5,
            source_code=source_1.id,
        ),
        name="print",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=4,
                end_lineno=2,
                end_col_offset=14,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=4,
                    end_lineno=2,
                    end_col_offset=7,
                    source_code=source_1.id,
                ),
                name="min",
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
                        source_location=SourceLocation(
                            lineno=1,
                            col_offset=4,
                            end_lineno=1,
                            end_col_offset=7,
                            source_code=source_1.id,
                        ),
                        name="abs",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=8,
                                end_lineno=1,
                                end_col_offset=10,
                                source_code=source_1.id,
                            ),
                            value=11,
                        ).id
                    ],
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=11,
                        end_lineno=2,
                        end_col_offset=13,
                        source_code=source_1.id,
                    ),
                    value=10,
                ).id,
            ],
        ).id
    ],
)
