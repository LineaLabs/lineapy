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
call_5 = CallNode(
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
            call_id=CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=4,
                    end_col_offset=15,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_exec_statement",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""if True:
    x.append(1)""",
                    ).id
                ],
                global_reads={"x": call_2.id},
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
