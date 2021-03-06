import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""name="marcelo"
it=iter(name)
print(next(it))
print(*it)
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=3,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=2,
            col_offset=3,
            end_lineno=2,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        name="iter",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=5,
                end_lineno=1,
                end_col_offset=14,
                source_code=source_1.id,
            ),
            value="marcelo",
        ).id
    ],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=0,
            end_lineno=3,
            end_col_offset=5,
            source_code=source_1.id,
        ),
        name="print",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=6,
                end_lineno=3,
                end_col_offset=14,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=6,
                    end_lineno=3,
                    end_col_offset=10,
                    source_code=source_1.id,
                ),
                name="next",
            ).id,
            positional_args=[call_1.id],
        ).id
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=0,
            end_lineno=4,
            end_col_offset=5,
            source_code=source_1.id,
        ),
        name="print",
    ).id,
    positional_args=[*call_1.id],
)
