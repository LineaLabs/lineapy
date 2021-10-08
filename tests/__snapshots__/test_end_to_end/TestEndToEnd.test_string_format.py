import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="a = '{{ {0} }}'.format('foo')",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=4,
            end_lineno=1,
            end_col_offset=22,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            LiteralNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=4,
                    end_lineno=1,
                    end_col_offset=15,
                    source_code=source_1.id,
                ),
                value="{{ {0} }}",
            ).id,
            LiteralNode(
                value="format",
            ).id,
        ],
        keyword_args={},
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=23,
                end_lineno=1,
                end_col_offset=28,
                source_code=source_1.id,
            ),
            value="foo",
        ).id
    ],
    keyword_args={},
)
