import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = []
x.append(10)

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
    library=Library(
        name="lineapy",
    ),
)
call_1 = CallNode(
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
mutate_2 = MutateNode(
    source_id=import_1.id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=0,
            end_lineno=5,
            end_col_offset=20,
            source_code=source_1.id,
        ),
        function_id=CallNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=0,
                end_lineno=5,
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
            MutateNode(
                source_id=call_1.id,
                call_id=CallNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=0,
                        end_lineno=3,
                        end_col_offset=12,
                        source_code=source_1.id,
                    ),
                    function_id=CallNode(
                        source_location=SourceLocation(
                            lineno=3,
                            col_offset=0,
                            end_lineno=3,
                            end_col_offset=8,
                            source_code=source_1.id,
                        ),
                        function_id=LookupNode(
                            name="getattr",
                        ).id,
                        positional_args=[
                            call_1.id,
                            LiteralNode(
                                value="append",
                            ).id,
                        ],
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=3,
                                col_offset=9,
                                end_lineno=3,
                                end_col_offset=11,
                                source_code=source_1.id,
                            ),
                            value=10,
                        ).id
                    ],
                ).id,
            ).id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=5,
                    col_offset=16,
                    end_lineno=5,
                    end_col_offset=19,
                    source_code=source_1.id,
                ),
                value="x",
            ).id,
        ],
    ).id,
)
