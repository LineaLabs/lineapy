import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = 1
res = lineapy.save(x, "x")
slice = res.get_code()
value = res.get_value()
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
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=6,
        end_lineno=3,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=6,
            end_lineno=3,
            end_col_offset=18,
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
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=4,
                end_lineno=2,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=22,
                end_lineno=3,
                end_col_offset=25,
                source_code=source_1.id,
            ),
            value="x",
        ).id,
    ],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=8,
            end_lineno=4,
            end_col_offset=20,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_3.id,
            LiteralNode(
                value="get_code",
            ).id,
        ],
    ).id,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=8,
        end_lineno=5,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=8,
            end_lineno=5,
            end_col_offset=21,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_3.id,
            LiteralNode(
                value="get_value",
            ).id,
        ],
    ).id,
)
