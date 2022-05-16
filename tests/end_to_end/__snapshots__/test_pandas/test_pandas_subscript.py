import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
df["C"] = df["A"] + df["B"]

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
                            value="A",
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
                            value="B",
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
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=10,
        end_lineno=4,
        end_col_offset=17,
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
                col_offset=13,
                end_lineno=4,
                end_col_offset=16,
                source_code=source_1.id,
            ),
            value="A",
        ).id,
    ],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=20,
        end_lineno=4,
        end_col_offset=27,
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
                col_offset=23,
                end_lineno=4,
                end_col_offset=26,
                source_code=source_1.id,
            ),
            value="B",
        ).id,
    ],
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setitem",
    ).id,
    positional_args=[
        call_9.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=3,
                end_lineno=4,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            value="C",
        ).id,
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=10,
                end_lineno=4,
                end_col_offset=27,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="add",
            ).id,
            positional_args=[call_10.id, call_11.id],
        ).id,
    ],
)
mutate_2 = MutateNode(
    source_id=call_11.id,
    call_id=call_13.id,
)
mutate_3 = MutateNode(
    source_id=call_10.id,
    call_id=call_13.id,
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=6,
            col_offset=0,
            end_lineno=6,
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
            call_id=call_13.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=17,
                end_lineno=6,
                end_col_offset=21,
                source_code=source_1.id,
            ),
            value="df",
        ).id,
    ],
)
