import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="sqrt",
)
literal_2 = LiteralNode(
    value="math",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="pow",
)
source_1 = SourceCode(
    code="""from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    name="math",
    version="",
    package_name="math",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_3.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=10,
        end_lineno=2,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value=5,
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=13,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    value=2,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=call_2.id,
    positional_args=[literal_4.id, literal_5.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[call_4.id],
)
