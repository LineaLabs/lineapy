import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""list_1 = [1,2,3,4]
cubed = map(lambda x: pow(x,3), list_1)
final_value = list(cubed)""",
    location=PosixPath("[source file path]"),
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=14,
        end_lineno=3,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=14,
            end_lineno=3,
            end_col_offset=18,
            source_code=source_1.id,
        ),
        name="list",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=8,
                end_lineno=2,
                end_col_offset=39,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=8,
                    end_lineno=2,
                    end_col_offset=11,
                    source_code=source_1.id,
                ),
                name="map",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=12,
                        end_lineno=2,
                        end_col_offset=30,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_exec_expr",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="lambda x: pow(x,3)",
                        ).id
                    ],
                ).id,
                CallNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=9,
                        end_lineno=1,
                        end_col_offset=18,
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
                    ],
                ).id,
            ],
        ).id
    ],
)
