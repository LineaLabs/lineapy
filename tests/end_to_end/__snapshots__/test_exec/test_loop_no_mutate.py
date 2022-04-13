import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
xs = [[]]
for x in xs:
    pass

lineapy.save(x, \'x\')
lineapy.save(xs, \'xs\')
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
    version="0.0.1",
    package_name="lineapy",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=6,
                end_lineno=2,
                end_col_offset=8,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
        ).id
    ],
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
            import_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        GlobalNode(
            name="x",
            call_id=CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=4,
                    end_col_offset=8,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_exec_statement",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""for x in xs:
    pass""",
                    ).id
                ],
                global_reads={"xs": call_2.id},
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
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=0,
            end_lineno=7,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=17,
                end_lineno=7,
                end_col_offset=21,
                source_code=source_1.id,
            ),
            value="xs",
        ).id,
    ],
)
