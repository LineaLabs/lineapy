import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""def func():
    for i in range(3):
        for j in range(3):
            yield (i,j), 10

ind, patch = zip(*func())""",
    location=PosixPath("[source file path]"),
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_unpack_sequence",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=13,
                end_lineno=6,
                end_col_offset=25,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=6,
                    col_offset=13,
                    end_lineno=6,
                    end_col_offset=16,
                    source_code=source_1.id,
                ),
                name="zip",
            ).id,
            positional_args=[
                *CallNode(
                    source_location=SourceLocation(
                        lineno=6,
                        col_offset=18,
                        end_lineno=6,
                        end_col_offset=24,
                        source_code=source_1.id,
                    ),
                    function_id=GlobalNode(
                        name="func",
                        call_id=CallNode(
                            source_location=SourceLocation(
                                lineno=1,
                                col_offset=0,
                                end_lineno=4,
                                end_col_offset=27,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="l_exec_statement",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="""def func():
    for i in range(3):
        for j in range(3):
            yield (i,j), 10""",
                                ).id
                            ],
                        ).id,
                    ).id,
                ).id
            ],
        ).id,
        LiteralNode(
            value=2,
        ).id,
    ],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_4.id,
        LiteralNode(
            value=1,
        ).id,
    ],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_4.id,
        LiteralNode(
            value=0,
        ).id,
    ],
)
