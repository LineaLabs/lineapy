import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""list_1 = [1,2,3,4,5,6,7,8,9]
list_2 = list(filter(lambda x: x%2==0, list_1))
""",
    location=PosixPath("[source file path]"),
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=9,
        end_lineno=2,
        end_col_offset=47,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="list",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=14,
                end_lineno=2,
                end_col_offset=46,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="filter",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=21,
                        end_lineno=2,
                        end_col_offset=37,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_exec_expr",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="lambda x: x%2==0",
                        ).id
                    ],
                ).id,
                CallNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=9,
                        end_lineno=1,
                        end_col_offset=28,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_list",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=10,
                                end_lineno=1,
                                end_col_offset=11,
                                source_code=source_1.id,
                            ),
                            value=1,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=12,
                                end_lineno=1,
                                end_col_offset=13,
                                source_code=source_1.id,
                            ),
                            value=2,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=14,
                                end_lineno=1,
                                end_col_offset=15,
                                source_code=source_1.id,
                            ),
                            value=3,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=16,
                                end_lineno=1,
                                end_col_offset=17,
                                source_code=source_1.id,
                            ),
                            value=4,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=18,
                                end_lineno=1,
                                end_col_offset=19,
                                source_code=source_1.id,
                            ),
                            value=5,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=20,
                                end_lineno=1,
                                end_col_offset=21,
                                source_code=source_1.id,
                            ),
                            value=6,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=22,
                                end_lineno=1,
                                end_col_offset=23,
                                source_code=source_1.id,
                            ),
                            value=7,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=24,
                                end_lineno=1,
                                end_col_offset=25,
                                source_code=source_1.id,
                            ),
                            value=8,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=26,
                                end_lineno=1,
                                end_col_offset=27,
                                source_code=source_1.id,
                            ),
                            value=9,
                        ).id,
                    ],
                ).id,
            ],
        ).id
    ],
)
