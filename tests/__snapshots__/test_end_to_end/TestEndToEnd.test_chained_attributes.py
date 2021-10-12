import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="import altair; altair.data_transformers.enable('json')",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=15,
        end_lineno=1,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=15,
            end_lineno=1,
            end_col_offset=46,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=15,
                    end_lineno=1,
                    end_col_offset=39,
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
                            end_col_offset=13,
                            source_code=source_1.id,
                        ),
                        library=Library(
                            name="altair",
                        ),
                    ).id,
                    LiteralNode(
                        value="data_transformers",
                    ).id,
                ],
            ).id,
            LiteralNode(
                value="enable",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=47,
                end_lineno=1,
                end_col_offset=53,
                source_code=source_1.id,
            ),
            value="json",
        ).id
    ],
)
