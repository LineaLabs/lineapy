import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import pandas as pd
assert pd.__name__ == \'pandas\'""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_assert",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=7,
                end_lineno=2,
                end_col_offset=30,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="eq",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=7,
                        end_lineno=2,
                        end_col_offset=18,
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
                                end_col_offset=19,
                                source_code=source_1.id,
                            ),
                            name="pandas",
                            version="",
                            package_name="pandas",
                        ).id,
                        LiteralNode(
                            value="__name__",
                        ).id,
                    ],
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=22,
                        end_lineno=2,
                        end_col_offset=30,
                        source_code=source_1.id,
                    ),
                    value="pandas",
                ).id,
            ],
        ).id
    ],
)
