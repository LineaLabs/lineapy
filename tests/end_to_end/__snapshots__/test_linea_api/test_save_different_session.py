import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
lineapy.save(10, \'x\')""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=2,
            col_offset=0,
            end_lineno=2,
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
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=13,
                end_lineno=2,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            value=10,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=17,
                end_lineno=2,
                end_col_offset=20,
                source_code=source_1.id,
            ),
            value="x",
        ).id,
    ],
)
