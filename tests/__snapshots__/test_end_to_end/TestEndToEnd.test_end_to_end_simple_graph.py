import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = abs(11)
lineapy.linea_publish(a, \'testing artifact publish\')
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
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="abs",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=8,
                end_lineno=2,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=11,
        ).id
    ],
    keyword_args={},
)
