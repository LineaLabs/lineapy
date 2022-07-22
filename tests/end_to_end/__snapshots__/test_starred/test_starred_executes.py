import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""def func(a,b):
    return a+b

args = {\'a\':1, \'b\':2}
ret = func(**args)
""",
    location=PosixPath("[source file path]"),
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=6,
        end_lineno=5,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="func",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=0,
                end_lineno=2,
                end_col_offset=14,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_exec_statement",
            ).id,
            positional_args=[
                LiteralNode(
                    value="""def func(a,b):
    return a+b""",
                ).id
            ],
        ).id,
    ).id,
    keyword_args={
        "**": CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=7,
                end_lineno=4,
                end_col_offset=21,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_dict",
            ).id,
            positional_args=[
                CallNode(
                    function_id=LookupNode(
                        name="l_tuple",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=8,
                                end_lineno=4,
                                end_col_offset=11,
                                source_code=source_1.id,
                            ),
                            value="a",
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=12,
                                end_lineno=4,
                                end_col_offset=13,
                                source_code=source_1.id,
                            ),
                            value=1,
                        ).id,
                    ],
                ).id,
                CallNode(
                    function_id=LookupNode(
                        name="l_tuple",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=15,
                                end_lineno=4,
                                end_col_offset=18,
                                source_code=source_1.id,
                            ),
                            value="b",
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=19,
                                end_lineno=4,
                                end_col_offset=20,
                                source_code=source_1.id,
                            ),
                            value=2,
                        ).id,
                    ],
                ).id,
            ],
        ).id
    },
)
