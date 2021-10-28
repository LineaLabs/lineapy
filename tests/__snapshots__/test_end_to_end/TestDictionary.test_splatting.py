import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="x = {1: 2, 2:2, **{1: 3, 2: 3}, 1: 4}",
    location=PosixPath("[source file path]"),
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=37,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_dict",
    ).id,
    positional_args=[
        CallNode(
            function_id=LookupNode(
                name="l_tuple",
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
                        col_offset=8,
                        end_lineno=1,
                        end_col_offset=9,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id,
        CallNode(
            function_id=LookupNode(
                name="l_tuple",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=11,
                        end_lineno=1,
                        end_col_offset=12,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=13,
                        end_lineno=1,
                        end_col_offset=14,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id,
        CallNode(
            function_id=LookupNode(
                name="l_tuple",
            ).id,
            positional_args=[
                CallNode(
                    function_id=LookupNode(
                        name="l_dict_kwargs_sentinel",
                    ).id,
                ).id,
                CallNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=18,
                        end_lineno=1,
                        end_col_offset=30,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_dict",
                    ).id,
                    positional_args=[
                        CallNode(
                            function_id=LookupNode(
                                name="l_tuple",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=1,
                                        col_offset=19,
                                        end_lineno=1,
                                        end_col_offset=20,
                                        source_code=source_1.id,
                                    ),
                                    value=1,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=1,
                                        col_offset=22,
                                        end_lineno=1,
                                        end_col_offset=23,
                                        source_code=source_1.id,
                                    ),
                                    value=3,
                                ).id,
                            ],
                        ).id,
                        CallNode(
                            function_id=LookupNode(
                                name="l_tuple",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=1,
                                        col_offset=25,
                                        end_lineno=1,
                                        end_col_offset=26,
                                        source_code=source_1.id,
                                    ),
                                    value=2,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=1,
                                        col_offset=28,
                                        end_lineno=1,
                                        end_col_offset=29,
                                        source_code=source_1.id,
                                    ),
                                    value=3,
                                ).id,
                            ],
                        ).id,
                    ],
                ).id,
            ],
        ).id,
        CallNode(
            function_id=LookupNode(
                name="l_tuple",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=32,
                        end_lineno=1,
                        end_col_offset=33,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=35,
                        end_lineno=1,
                        end_col_offset=36,
                        source_code=source_1.id,
                    ),
                    value=4,
                ).id,
            ],
        ).id,
    ],
)
