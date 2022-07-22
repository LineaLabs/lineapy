import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import matplotlib.pyplot as plt
x = plt.ylabel(\'label\')

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
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="matplotlib",
        ).id
    ],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    name="matplotlib.pyplot",
    version="",
    package_name="matplotlib",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="pyplot",
        ).id,
        call_2.id,
    ],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_3.id,
)
call_7 = CallNode(
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
        CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=4,
                end_lineno=3,
                end_col_offset=23,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=4,
                    end_lineno=3,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    call_3.id,
                    LiteralNode(
                        value="ylabel",
                    ).id,
                ],
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=15,
                        end_lineno=3,
                        end_col_offset=22,
                        source_code=source_1.id,
                    ),
                    value="label",
                ).id
            ],
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
)
