import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = []
if True:
    x.append(1)

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
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
)
if_else_1 = IfElseNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    test_id=LiteralNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=3,
            end_lineno=3,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        value=True,
    ).id,
)
call_6 = CallNode(
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
            control_dependency=if_else_1.id,
            source_id=call_2.id,
            call_id=CallNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=4,
                    end_lineno=4,
                    end_col_offset=15,
                    source_code=source_1.id,
                ),
                control_dependency=if_else_1.id,
                function_id=CallNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=4,
                        end_lineno=4,
                        end_col_offset=12,
                        source_code=source_1.id,
                    ),
                    control_dependency=if_else_1.id,
                    function_id=LookupNode(
                        control_dependency=if_else_1.id,
                        name="getattr",
                    ).id,
                    positional_args=[
                        call_2.id,
                        LiteralNode(
                            control_dependency=if_else_1.id,
                            value="append",
                        ).id,
                    ],
                ).id,
                positional_args=[
                    LiteralNode(
                        source_location=SourceLocation(
                            lineno=4,
                            col_offset=13,
                            end_lineno=4,
                            end_col_offset=14,
                            source_code=source_1.id,
                        ),
                        control_dependency=if_else_1.id,
                        value=1,
                    ).id
                ],
            ).id,
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
