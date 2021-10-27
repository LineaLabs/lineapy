import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import pandas as pd
df = pd.DataFrame({"id": [1,2]})
df["id"].sum()
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=25,
        end_lineno=2,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=26,
                end_lineno=2,
                end_col_offset=27,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=28,
                end_lineno=2,
                end_col_offset=29,
                source_code=source_1.id,
            ),
            value=2,
        ).id,
    ],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_2.id,
)
global_2 = GlobalNode(
    name="bs",
    call_id=call_2.id,
)
global_3 = GlobalNode(
    name="pandas",
    call_id=call_2.id,
)
global_4 = GlobalNode(
    name="new_df",
    call_id=call_2.id,
)
global_5 = GlobalNode(
    name="v",
    call_id=call_2.id,
)
global_6 = GlobalNode(
    name="b",
    call_id=call_2.id,
)
global_7 = GlobalNode(
    name="x",
    call_id=call_2.id,
)
global_8 = GlobalNode(
    name="c",
    call_id=call_2.id,
)
global_9 = GlobalNode(
    name="a",
    call_id=call_2.id,
)
global_10 = GlobalNode(
    name="my_function",
    call_id=call_2.id,
)
global_11 = GlobalNode(
    name="math",
    call_id=call_2.id,
)
global_12 = GlobalNode(
    name="df",
    call_id=call_2.id,
)
global_13 = GlobalNode(
    name="DataFrame",
    call_id=call_2.id,
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=0,
            end_lineno=3,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=3,
                    end_col_offset=8,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getitem",
                ).id,
                positional_args=[
                    CallNode(
                        source_location=SourceLocation(
                            lineno=2,
                            col_offset=5,
                            end_lineno=2,
                            end_col_offset=32,
                            source_code=source_1.id,
                        ),
                        function_id=CallNode(
                            source_location=SourceLocation(
                                lineno=2,
                                col_offset=5,
                                end_lineno=2,
                                end_col_offset=17,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                ImportNode(
                                    source_location=SourceLocation(
                                        lineno=1,
                                        col_offset=0,
                                        end_lineno=1,
                                        end_col_offset=19,
                                        source_code=source_1.id,
                                    ),
                                    library=Library(
                                        name="pandas",
                                    ),
                                ).id,
                                LiteralNode(
                                    value="DataFrame",
                                ).id,
                            ],
                        ).id,
                        positional_args=[
                            CallNode(
                                source_location=SourceLocation(
                                    lineno=2,
                                    col_offset=18,
                                    end_lineno=2,
                                    end_col_offset=31,
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
                                                    lineno=2,
                                                    col_offset=19,
                                                    end_lineno=2,
                                                    end_col_offset=23,
                                                    source_code=source_1.id,
                                                ),
                                                value="id",
                                            ).id,
                                            call_2.id,
                                        ],
                                    ).id
                                ],
                            ).id
                        ],
                    ).id,
                    LiteralNode(
                        source_location=SourceLocation(
                            lineno=3,
                            col_offset=3,
                            end_lineno=3,
                            end_col_offset=7,
                            source_code=source_1.id,
                        ),
                        value="id",
                    ).id,
                ],
            ).id,
            LiteralNode(
                value="sum",
            ).id,
        ],
    ).id,
)
