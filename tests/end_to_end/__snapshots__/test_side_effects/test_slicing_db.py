import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
import sqlite3
conn = sqlite3.connect(\':memory:\')
df.to_sql(name="test", con=conn,index=False)

lineapy.save(lineapy.db, \'lineapy.db\')
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
call_1 = CallNode(
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
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    name="sqlite3",
    version="",
    package_name="sqlite3",
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=38,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=8,
            col_offset=0,
            end_lineno=8,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=8,
                col_offset=13,
                end_lineno=8,
                end_col_offset=23,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                call_1.id,
                LiteralNode(
                    value="db",
                ).id,
            ],
            implicit_dependencies=[
                MutateNode(
                    source_id=LookupNode(
                        name="db",
                    ).id,
                    call_id=CallNode(
                        source_location=SourceLocation(
                            lineno=6,
                            col_offset=0,
                            end_lineno=6,
                            end_col_offset=44,
                            source_code=source_1.id,
                        ),
                        function_id=CallNode(
                            source_location=SourceLocation(
                                lineno=6,
                                col_offset=0,
                                end_lineno=6,
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
                                    value="to_sql",
                                ).id,
                            ],
                        ).id,
                        keyword_args={
                            "con": CallNode(
                                source_location=SourceLocation(
                                    lineno=5,
                                    col_offset=7,
                                    end_lineno=5,
                                    end_col_offset=34,
                                    source_code=source_1.id,
                                ),
                                function_id=CallNode(
                                    source_location=SourceLocation(
                                        lineno=5,
                                        col_offset=7,
                                        end_lineno=5,
                                        end_col_offset=22,
                                        source_code=source_1.id,
                                    ),
                                    function_id=LookupNode(
                                        name="getattr",
                                    ).id,
                                    positional_args=[
                                        CallNode(
                                            source_location=SourceLocation(
                                                lineno=4,
                                                col_offset=0,
                                                end_lineno=4,
                                                end_col_offset=14,
                                                source_code=source_1.id,
                                            ),
                                            function_id=LookupNode(
                                                name="l_import",
                                            ).id,
                                            positional_args=[
                                                LiteralNode(
                                                    value="sqlite3",
                                                ).id
                                            ],
                                        ).id,
                                        LiteralNode(
                                            value="connect",
                                        ).id,
                                    ],
                                ).id,
                                positional_args=[
                                    LiteralNode(
                                        source_location=SourceLocation(
                                            lineno=5,
                                            col_offset=23,
                                            end_lineno=5,
                                            end_col_offset=33,
                                            source_code=source_1.id,
                                        ),
                                        value=":memory:",
                                    ).id
                                ],
                            ).id,
                            "index": LiteralNode(
                                source_location=SourceLocation(
                                    lineno=6,
                                    col_offset=38,
                                    end_lineno=6,
                                    end_col_offset=43,
                                    source_code=source_1.id,
                                ),
                                value=False,
                            ).id,
                            "name": LiteralNode(
                                source_location=SourceLocation(
                                    lineno=6,
                                    col_offset=15,
                                    end_lineno=6,
                                    end_col_offset=21,
                                    source_code=source_1.id,
                                ),
                                value="test",
                            ).id,
                        },
                    ).id,
                ).id
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=8,
                col_offset=25,
                end_lineno=8,
                end_col_offset=37,
                source_code=source_1.id,
            ),
            value="lineapy.db",
        ).id,
    ],
)
