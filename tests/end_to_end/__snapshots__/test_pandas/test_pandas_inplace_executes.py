import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"A": [2, 4, None], "B": [4, 5, 6]})
mdf = df[\'A\'].mean()
df[\'A\'].fillna(mdf, inplace=True)

lineapy.save(df, \'df\')
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    name="lineapy",
    version="",
    package_name="lineapy",
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    name="pandas",
    version="",
    package_name="pandas",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=5,
        end_lineno=3,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=5,
            end_lineno=3,
            end_col_offset=17,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=0,
                    end_lineno=2,
                    end_col_offset=19,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_import",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="pandas",
                    ).id
                ],
            ).id,
            LiteralNode(
                value="DataFrame",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=18,
                end_lineno=3,
                end_col_offset=53,
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
                                lineno=3,
                                col_offset=19,
                                end_lineno=3,
                                end_col_offset=22,
                                source_code=source_1.id,
                            ),
                            value="A",
                        ).id,
                        CallNode(
                            source_location=SourceLocation(
                                lineno=3,
                                col_offset=24,
                                end_lineno=3,
                                end_col_offset=36,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="l_list",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=25,
                                        end_lineno=3,
                                        end_col_offset=26,
                                        source_code=source_1.id,
                                    ),
                                    value=2,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=28,
                                        end_lineno=3,
                                        end_col_offset=29,
                                        source_code=source_1.id,
                                    ),
                                    value=4,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=31,
                                        end_lineno=3,
                                        end_col_offset=35,
                                        source_code=source_1.id,
                                    ),
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
                                lineno=3,
                                col_offset=38,
                                end_lineno=3,
                                end_col_offset=41,
                                source_code=source_1.id,
                            ),
                            value="B",
                        ).id,
                        CallNode(
                            source_location=SourceLocation(
                                lineno=3,
                                col_offset=43,
                                end_lineno=3,
                                end_col_offset=52,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="l_list",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=44,
                                        end_lineno=3,
                                        end_col_offset=45,
                                        source_code=source_1.id,
                                    ),
                                    value=4,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=47,
                                        end_lineno=3,
                                        end_col_offset=48,
                                        source_code=source_1.id,
                                    ),
                                    value=5,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=50,
                                        end_lineno=3,
                                        end_col_offset=51,
                                        source_code=source_1.id,
                                    ),
                                    value=6,
                                ).id,
                            ],
                        ).id,
                    ],
                ).id,
            ],
        ).id
    ],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=6,
        end_lineno=4,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_9.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=9,
                end_lineno=4,
                end_col_offset=12,
                source_code=source_1.id,
            ),
            value="A",
        ).id,
    ],
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_9.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=3,
                end_lineno=5,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            value="A",
        ).id,
    ],
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=0,
            end_lineno=5,
            end_col_offset=14,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_13.id,
            LiteralNode(
                value="fillna",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=6,
                end_lineno=4,
                end_col_offset=20,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=6,
                    end_lineno=4,
                    end_col_offset=18,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    call_10.id,
                    LiteralNode(
                        value="mean",
                    ).id,
                ],
            ).id,
        ).id
    ],
    keyword_args={
        "inplace": LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=28,
                end_lineno=5,
                end_col_offset=32,
                source_code=source_1.id,
            ),
            value=True,
        ).id
    },
)
mutate_2 = MutateNode(
    source_id=call_10.id,
    call_id=call_15.id,
)
mutate_3 = MutateNode(
    source_id=call_13.id,
    call_id=call_15.id,
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=0,
            end_lineno=7,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_import",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="lineapy",
                    ).id
                ],
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        MutateNode(
            source_id=call_9.id,
            call_id=call_15.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=17,
                end_lineno=7,
                end_col_offset=21,
                source_code=source_1.id,
            ),
            value="df",
        ).id,
    ],
)
