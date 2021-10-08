import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="import types; x = types.SimpleNamespace(); x.hi = 1; del x.hi",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=18,
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
                    end_col_offset=12,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="types",
                ),
            ).id,
            LiteralNode(
                value="SimpleNamespace",
            ).id,
        ],
        keyword_args={},
    ).id,
    positional_args=[],
    keyword_args={},
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=43,
        end_lineno=1,
        end_col_offset=51,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setattr",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            value="hi",
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=50,
                end_lineno=1,
                end_col_offset=51,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
    ],
    keyword_args={},
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=53,
        end_lineno=1,
        end_col_offset=61,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="delattr",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            value="hi",
        ).id,
    ],
    keyword_args={},
)
