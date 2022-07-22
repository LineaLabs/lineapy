import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = [1, 2, 3]
if b := a.pop():
    b += 1

lineapy.save(a, \'a\')
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
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=5,
                end_lineno=2,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=8,
                end_lineno=2,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            value=2,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=11,
                end_lineno=2,
                end_col_offset=12,
                source_code=source_1.id,
            ),
            value=3,
        ).id,
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=8,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=8,
            end_lineno=3,
            end_col_offset=13,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_2.id,
            LiteralNode(
                value="pop",
            ).id,
        ],
    ).id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_alias",
    ).id,
    positional_args=[call_4.id],
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    test_id=call_5.id,
)
global_1 = GlobalNode(
    control_dependency=if_1.id,
    name="b",
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=4,
            end_lineno=4,
            end_col_offset=10,
            source_code=source_1.id,
        ),
        control_dependency=if_1.id,
        function_id=LookupNode(
            control_dependency=if_1.id,
            name="l_exec_statement",
        ).id,
        positional_args=[
            LiteralNode(
                control_dependency=if_1.id,
                value="b += 1",
            ).id
        ],
        global_reads={"b": call_5.id},
    ).id,
)
call_8 = CallNode(
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
            source_id=call_2.id,
            call_id=call_4.id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=16,
                end_lineno=6,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
    ],
)
