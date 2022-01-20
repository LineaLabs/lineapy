import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import pandas, numpy
c = pandas.DataFrame()
d = numpy.array([1,2,3])
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=2,
            col_offset=4,
            end_lineno=2,
            end_col_offset=20,
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
                    end_col_offset=20,
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
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=4,
            end_lineno=3,
            end_col_offset=15,
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
                    end_col_offset=20,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="numpy",
                ),
            ).id,
            LiteralNode(
                value="array",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=16,
                end_lineno=3,
                end_col_offset=23,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=17,
                        end_lineno=3,
                        end_col_offset=18,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=19,
                        end_lineno=3,
                        end_col_offset=20,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=21,
                        end_lineno=3,
                        end_col_offset=22,
                        source_code=source_1.id,
                    ),
                    value=3,
                ).id,
            ],
        ).id
    ],
)
