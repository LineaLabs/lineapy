import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
from functools import lru_cache
@lru_cache(maxsize=1)
def f():
    return 1

x = f()

lineapy.save(x, \'x\')
""",
    location=PosixPath("[source file path]"),
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=9,
            col_offset=0,
            end_lineno=9,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
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
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=4,
                end_lineno=7,
                end_col_offset=7,
                source_code=source_1.id,
            ),
            function_id=GlobalNode(
                name="f",
                call_id=CallNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=0,
                        end_lineno=5,
                        end_col_offset=12,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_exec_statement",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="""@lru_cache(maxsize=1)
def f():
    return 1""",
                        ).id
                    ],
                    global_reads={
                        "lru_cache": CallNode(
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                ImportNode(
                                    source_location=SourceLocation(
                                        lineno=2,
                                        col_offset=0,
                                        end_lineno=2,
                                        end_col_offset=31,
                                        source_code=source_1.id,
                                    ),
                                    name="functools",
                                    version="",
                                    package_name="functools",
                                ).id,
                                LiteralNode(
                                    value="lru_cache",
                                ).id,
                            ],
                        ).id
                    },
                ).id,
            ).id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=16,
                end_lineno=9,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="x",
        ).id,
    ],
)
