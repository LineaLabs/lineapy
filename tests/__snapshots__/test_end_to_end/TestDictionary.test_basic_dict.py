import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="x = {'a': 1, 'b': 2}",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_dict__",
    ).id,
    positional_args=[
        CallNode(
            function_id=LookupNode(
                name="__build_tuple__",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=5,
                        end_lineno=1,
                        end_col_offset=8,
                        source_code=source_1.id,
                    ),
                    value="a",
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=10,
                        end_lineno=1,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
            ],
        ).id,
        CallNode(
            function_id=LookupNode(
                name="__build_tuple__",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=13,
                        end_lineno=1,
                        end_col_offset=16,
                        source_code=source_1.id,
                    ),
                    value="b",
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=18,
                        end_lineno=1,
                        end_col_offset=19,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id,
    ],
)
