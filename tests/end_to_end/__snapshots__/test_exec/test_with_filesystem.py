import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
from tempfile import TemporaryFile
with TemporaryFile() as f:
    f.write(b\'some lines\')

lineapy.save(lineapy.file_system, \'lineapy.file_system\')
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
call_1 = CallNode(
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
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    name="tempfile",
    version="",
    package_name="tempfile",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_exec_statement",
    ).id,
    positional_args=[
        LiteralNode(
            value="""with TemporaryFile() as f:
    f.write(b\'some lines\')""",
        ).id
    ],
    global_reads={
        "TemporaryFile": CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=0,
                end_lineno=2,
                end_col_offset=34,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=0,
                        end_lineno=2,
                        end_col_offset=34,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_import",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="tempfile",
                        ).id
                    ],
                ).id,
                LiteralNode(
                    value="TemporaryFile",
                ).id,
            ],
        ).id
    },
)
global_1 = GlobalNode(
    name="f",
    call_id=call_4.id,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=56,
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
            call_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=13,
                end_lineno=6,
                end_col_offset=32,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                call_1.id,
                LiteralNode(
                    value="file_system",
                ).id,
            ],
            implicit_dependencies=[
                MutateNode(
                    source_id=LookupNode(
                        name="file_system",
                    ).id,
                    call_id=call_4.id,
                ).id
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=34,
                end_lineno=6,
                end_col_offset=55,
                source_code=source_1.id,
            ),
            value="lineapy.file_system",
        ).id,
    ],
)
