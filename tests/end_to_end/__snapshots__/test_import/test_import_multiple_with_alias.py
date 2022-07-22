import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    name="math",
    version="",
    package_name="math",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="math",
        ).id
    ],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=43,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value="sqrt",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=4,
                end_lineno=2,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=43,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    call_1.id,
                    LiteralNode(
                        value="pow",
                    ).id,
                ],
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=10,
                        end_lineno=2,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    value=5,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=13,
                        end_lineno=2,
                        end_col_offset=14,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id
    ],
)
