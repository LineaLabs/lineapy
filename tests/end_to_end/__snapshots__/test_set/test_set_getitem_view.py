import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
y = set()
x = [y]
y.add(10)

lineapy.save(x, \'x\')
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=2,
            col_offset=4,
            end_lineno=2,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        name="set",
    ).id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=0,
            end_lineno=4,
            end_col_offset=5,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_2.id,
            LiteralNode(
                value="add",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=6,
                end_lineno=4,
                end_col_offset=8,
                source_code=source_1.id,
            ),
            value=10,
        ).id
    ],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_5.id,
)
call_7 = CallNode(
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
        MutateNode(
            source_id=CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=4,
                    end_lineno=3,
                    end_col_offset=7,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_list",
                ).id,
                positional_args=[call_2.id],
            ).id,
            call_id=call_5.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=16,
                end_lineno=6,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="x",
        ).id,
    ],
)
