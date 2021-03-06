import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_csv("test.csv", index=False)

df2 = pd.read_csv("test.csv")
df2["c"] = df2["a"] + df2["b"]
df2.to_csv("test2.csv", index=False)

df3 = pd.read_csv("test.csv")

lineapy.save(df3, \'df3\')
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
call_2 = CallNode(
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
)
mutate_1 = MutateNode(
    source_id=LookupNode(
        name="file_system",
    ).id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=0,
            end_lineno=4,
            end_col_offset=34,
            source_code=source_1.id,
        ),
        function_id=CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=0,
                end_lineno=4,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=5,
                        end_lineno=3,
                        end_col_offset=51,
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
                            call_2.id,
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
                                end_col_offset=50,
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
                                            value="a",
                                        ).id,
                                        CallNode(
                                            source_location=SourceLocation(
                                                lineno=3,
                                                col_offset=24,
                                                end_lineno=3,
                                                end_col_offset=33,
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
                                                    value=1,
                                                ).id,
                                                LiteralNode(
                                                    source_location=SourceLocation(
                                                        lineno=3,
                                                        col_offset=28,
                                                        end_lineno=3,
                                                        end_col_offset=29,
                                                        source_code=source_1.id,
                                                    ),
                                                    value=2,
                                                ).id,
                                                LiteralNode(
                                                    source_location=SourceLocation(
                                                        lineno=3,
                                                        col_offset=31,
                                                        end_lineno=3,
                                                        end_col_offset=32,
                                                        source_code=source_1.id,
                                                    ),
                                                    value=3,
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
                                                col_offset=35,
                                                end_lineno=3,
                                                end_col_offset=38,
                                                source_code=source_1.id,
                                            ),
                                            value="b",
                                        ).id,
                                        CallNode(
                                            source_location=SourceLocation(
                                                lineno=3,
                                                col_offset=40,
                                                end_lineno=3,
                                                end_col_offset=49,
                                                source_code=source_1.id,
                                            ),
                                            function_id=LookupNode(
                                                name="l_list",
                                            ).id,
                                            positional_args=[
                                                LiteralNode(
                                                    source_location=SourceLocation(
                                                        lineno=3,
                                                        col_offset=41,
                                                        end_lineno=3,
                                                        end_col_offset=42,
                                                        source_code=source_1.id,
                                                    ),
                                                    value=4,
                                                ).id,
                                                LiteralNode(
                                                    source_location=SourceLocation(
                                                        lineno=3,
                                                        col_offset=44,
                                                        end_lineno=3,
                                                        end_col_offset=45,
                                                        source_code=source_1.id,
                                                    ),
                                                    value=5,
                                                ).id,
                                                LiteralNode(
                                                    source_location=SourceLocation(
                                                        lineno=3,
                                                        col_offset=47,
                                                        end_lineno=3,
                                                        end_col_offset=48,
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
                ).id,
                LiteralNode(
                    value="to_csv",
                ).id,
            ],
        ).id,
        positional_args=[
            LiteralNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=10,
                    end_lineno=4,
                    end_col_offset=20,
                    source_code=source_1.id,
                ),
                value="test.csv",
            ).id
        ],
        keyword_args={
            "index": LiteralNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=28,
                    end_lineno=4,
                    end_col_offset=33,
                    source_code=source_1.id,
                ),
                value=False,
            ).id
        },
    ).id,
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=6,
        end_lineno=6,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=6,
            col_offset=6,
            end_lineno=6,
            end_col_offset=17,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_2.id,
            LiteralNode(
                value="read_csv",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=18,
                end_lineno=6,
                end_col_offset=28,
                source_code=source_1.id,
            ),
            value="test.csv",
        ).id
    ],
    implicit_dependencies=[mutate_1.id],
)
call_14 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=11,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_13.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=15,
                end_lineno=7,
                end_col_offset=18,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
    ],
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=22,
        end_lineno=7,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_13.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=26,
                end_lineno=7,
                end_col_offset=29,
                source_code=source_1.id,
            ),
            value="b",
        ).id,
    ],
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setitem",
    ).id,
    positional_args=[
        call_13.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=4,
                end_lineno=7,
                end_col_offset=7,
                source_code=source_1.id,
            ),
            value="c",
        ).id,
        CallNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=11,
                end_lineno=7,
                end_col_offset=30,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="add",
            ).id,
            positional_args=[call_14.id, call_15.id],
        ).id,
    ],
)
mutate_2 = MutateNode(
    source_id=call_15.id,
    call_id=call_17.id,
)
mutate_3 = MutateNode(
    source_id=call_14.id,
    call_id=call_17.id,
)
call_23 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=12,
            col_offset=0,
            end_lineno=12,
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
        CallNode(
            source_location=SourceLocation(
                lineno=10,
                col_offset=6,
                end_lineno=10,
                end_col_offset=29,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                source_location=SourceLocation(
                    lineno=10,
                    col_offset=6,
                    end_lineno=10,
                    end_col_offset=17,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    call_2.id,
                    LiteralNode(
                        value="read_csv",
                    ).id,
                ],
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=10,
                        col_offset=18,
                        end_lineno=10,
                        end_col_offset=28,
                        source_code=source_1.id,
                    ),
                    value="test.csv",
                ).id
            ],
            implicit_dependencies=[
                MutateNode(
                    source_id=mutate_1.id,
                    call_id=CallNode(
                        source_location=SourceLocation(
                            lineno=8,
                            col_offset=0,
                            end_lineno=8,
                            end_col_offset=36,
                            source_code=source_1.id,
                        ),
                        function_id=CallNode(
                            source_location=SourceLocation(
                                lineno=8,
                                col_offset=0,
                                end_lineno=8,
                                end_col_offset=10,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                MutateNode(
                                    source_id=call_13.id,
                                    call_id=call_17.id,
                                ).id,
                                LiteralNode(
                                    value="to_csv",
                                ).id,
                            ],
                        ).id,
                        positional_args=[
                            LiteralNode(
                                source_location=SourceLocation(
                                    lineno=8,
                                    col_offset=11,
                                    end_lineno=8,
                                    end_col_offset=22,
                                    source_code=source_1.id,
                                ),
                                value="test2.csv",
                            ).id
                        ],
                        keyword_args={
                            "index": LiteralNode(
                                source_location=SourceLocation(
                                    lineno=8,
                                    col_offset=30,
                                    end_lineno=8,
                                    end_col_offset=35,
                                    source_code=source_1.id,
                                ),
                                value=False,
                            ).id
                        },
                    ).id,
                ).id
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=12,
                col_offset=18,
                end_lineno=12,
                end_col_offset=23,
                source_code=source_1.id,
            ),
            value="df3",
        ).id,
    ],
)
