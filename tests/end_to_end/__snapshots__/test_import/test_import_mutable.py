import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import pandas
pandas.x = 1
y = pandas.x

lineapy.save(y, \'y\')
""",
    location=PosixPath("[source file path]"),
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    library=Library(
        name="pandas",
    ),
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=20,
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
            ImportNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="lineapy",
                ),
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=4,
                end_lineno=4,
                end_col_offset=12,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                MutateNode(
                    source_id=import_2.id,
                    call_id=CallNode(
                        source_location=SourceLocation(
                            lineno=3,
                            col_offset=0,
                            end_lineno=3,
                            end_col_offset=12,
                            source_code=source_1.id,
                        ),
                        function_id=LookupNode(
                            name="setattr",
                        ).id,
                        positional_args=[
                            import_2.id,
                            LiteralNode(
                                value="x",
                            ).id,
                            LiteralNode(
                                source_location=SourceLocation(
                                    lineno=3,
                                    col_offset=11,
                                    end_lineno=3,
                                    end_col_offset=12,
                                    source_code=source_1.id,
                                ),
                                value=1,
                            ).id,
                        ],
                    ).id,
                ).id,
                LiteralNode(
                    value="x",
                ).id,
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=16,
                end_lineno=6,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="y",
        ).id,
    ],
)
