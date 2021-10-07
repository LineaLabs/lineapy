import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = 1.2
b = a
""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=1.2,
)
