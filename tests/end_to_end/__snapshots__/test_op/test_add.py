import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""from decimal import Decimal
obj = Decimal(\'3.1415926535897932384626433832795028841971\')
assert +obj != obj""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    name="decimal",
    version="",
    package_name="decimal",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=6,
        end_lineno=2,
        end_col_offset=59,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=27,
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
                    end_col_offset=27,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_import",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="decimal",
                    ).id
                ],
            ).id,
            LiteralNode(
                value="Decimal",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=14,
                end_lineno=2,
                end_col_offset=58,
                source_code=source_1.id,
            ),
            value="3.1415926535897932384626433832795028841971",
        ).id
    ],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_assert",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=7,
                end_lineno=3,
                end_col_offset=18,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="ne",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=7,
                        end_lineno=3,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="pos",
                    ).id,
                    positional_args=[call_3.id],
                ).id,
                call_3.id,
            ],
        ).id
    ],
)
