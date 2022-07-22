import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="and_",
)
lookup_2 = LookupNode(
    name="or_",
)
lookup_3 = LookupNode(
    name="and_",
)
source_1 = SourceCode(
    code="""print(True and False)
print(True or False)
x = True and False
""",
    location=PosixPath("[source file path]"),
)
lookup_4 = LookupNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    name="print",
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=6,
        end_lineno=1,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=True,
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=15,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    value=False,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=6,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id, literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id],
)
lookup_5 = LookupNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    name="print",
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=6,
        end_lineno=2,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=True,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=14,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value=False,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=6,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_3.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value=True,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=13,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value=False,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_5.id, literal_6.id],
)
