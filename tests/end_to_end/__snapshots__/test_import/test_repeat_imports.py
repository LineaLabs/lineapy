import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
from math import pow
from math import sqrt
a=pow(5,2)
b=sqrt(a)

lineapy.linea_publish(a, \'a\')
lineapy.linea_publish(b, \'b\')
""",
    location=PosixPath("[source file path]"),
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=2,
        end_lineno=5,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=3,
                    end_col_offset=21,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="math",
                ),
            ).id,
            LiteralNode(
                value="sqrt",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=2,
                end_lineno=4,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    ImportNode(
                        source_location=SourceLocation(
                            lineno=2,
                            col_offset=0,
                            end_lineno=2,
                            end_col_offset=20,
                            source_code=source_1.id,
                        ),
                        library=Library(
                            name="math",
                        ),
                    ).id,
                    LiteralNode(
                        value="pow",
                    ).id,
                ],
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=6,
                        end_lineno=4,
                        end_col_offset=7,
                        source_code=source_1.id,
                    ),
                    value=5,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=8,
                        end_lineno=4,
                        end_col_offset=9,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id
    ],
)
