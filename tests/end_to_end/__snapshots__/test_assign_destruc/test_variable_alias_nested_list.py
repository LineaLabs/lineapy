import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""a = [0,1]
b = [a]
c = [b]""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=4,
                end_lineno=2,
                end_col_offset=7,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=4,
                        end_lineno=1,
                        end_col_offset=9,
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
                            value=0,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=7,
                                end_lineno=1,
                                end_col_offset=8,
                                source_code=source_1.id,
                            ),
                            value=1,
                        ).id,
                    ],
                ).id
            ],
        ).id
    ],
)
