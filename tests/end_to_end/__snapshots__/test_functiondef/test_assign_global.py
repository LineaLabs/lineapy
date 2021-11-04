import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
def f():
    global a
    a = 1
f()

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
    library=Library(
        name="lineapy",
    ),
)
mutate_1 = MutateNode(
    source_id=import_1.id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=0,
            end_lineno=7,
            end_col_offset=20,
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
            GlobalNode(
                name="a",
                call_id=CallNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=0,
                        end_lineno=5,
                        end_col_offset=3,
                        source_code=source_1.id,
                    ),
                    function_id=GlobalNode(
                        name="f",
                        call_id=CallNode(
                            source_location=SourceLocation(
                                lineno=2,
                                col_offset=0,
                                end_lineno=4,
                                end_col_offset=9,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="l_exec_statement",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="""def f():
    global a
    a = 1""",
                                ).id
                            ],
                        ).id,
                    ).id,
                ).id,
            ).id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=7,
                    col_offset=16,
                    end_lineno=7,
                    end_col_offset=19,
                    source_code=source_1.id,
                ),
                value="a",
            ).id,
        ],
    ).id,
)
