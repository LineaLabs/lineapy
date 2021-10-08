import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""bs = [1,2]
if len(bs) > 4:
    print("True")
else:
    bs.append(3)
    print("False")
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=6,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__exec__",
    ).id,
    positional_args=[
        LiteralNode(
            value="""if len(bs) > 4:
    print("True")
else:
    bs.append(3)
    print("False")""",
        ).id,
        LiteralNode(
            value=0,
        ).id,
    ],
    keyword_args={
        "bs": CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=5,
                end_lineno=1,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="__build_list__",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=6,
                        end_lineno=1,
                        end_col_offset=7,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=8,
                        end_lineno=1,
                        end_col_offset=9,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
            keyword_args={},
        ).id,
        "len": LookupNode(
            name="len",
        ).id,
        "print": LookupNode(
            name="print",
        ).id,
    },
)
