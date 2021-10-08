import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import pandas as pd
import lineapy

df = pd.read_csv(\'tests/simple_data.csv\')
s = df[\'a\'].sum()

lineapy.linea_publish(s, "Graph With CSV Import")
""",
    location=PosixPath("[source file path]"),
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    library=Library(
        name="lineapy",
    ),
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=4,
            end_lineno=5,
            end_col_offset=15,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=5,
                    col_offset=4,
                    end_lineno=5,
                    end_col_offset=11,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getitem",
                ).id,
                positional_args=[
                    CallNode(
                        source_location=SourceLocation(
                            lineno=4,
                            col_offset=5,
                            end_lineno=4,
                            end_col_offset=41,
                            source_code=source_1.id,
                        ),
                        function_id=CallNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=5,
                                end_lineno=4,
                                end_col_offset=16,
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
                                    value="read_csv",
                                ).id,
                            ],
                            keyword_args={},
                        ).id,
                        positional_args=[
                            LiteralNode(
                                source_location=SourceLocation(
                                    lineno=4,
                                    col_offset=17,
                                    end_lineno=4,
                                    end_col_offset=40,
                                    source_code=source_1.id,
                                ),
                                value="tests/simple_data.csv",
                            ).id
                        ],
                        keyword_args={},
                    ).id,
                    LiteralNode(
                        source_location=SourceLocation(
                            lineno=5,
                            col_offset=7,
                            end_lineno=5,
                            end_col_offset=10,
                            source_code=source_1.id,
                        ),
                        value="a",
                    ).id,
                ],
                keyword_args={},
            ).id,
            LiteralNode(
                value="sum",
            ).id,
        ],
        keyword_args={},
    ).id,
    positional_args=[],
    keyword_args={},
)
