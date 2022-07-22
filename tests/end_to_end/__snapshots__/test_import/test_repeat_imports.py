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
    value="pow",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="save",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="lineapy",
)
literal_4 = LiteralNode(
    value="math",
)
literal_5 = LiteralNode(
    value="sqrt",
)
lookup_5 = LookupNode(
    name="l_import",
)
lookup_6 = LookupNode(
    name="getattr",
)
literal_6 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
from math import pow
from math import sqrt
a=pow(5,2)
b=sqrt(a)

lineapy.save(a, \'a\')
lineapy.save(b, \'b\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_3.id],
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
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    name="math",
    version="",
    package_name="math",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_4.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_1.id],
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    name="math",
    version="",
    package_name="math",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_2.id, literal_5.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=6,
        end_lineno=4,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=5,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=8,
        end_lineno=4,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=2,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=2,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_7.id, literal_8.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=2,
        end_lineno=5,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=call_4.id,
    positional_args=[call_5.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_6.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=16,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="a",
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_7.id,
    positional_args=[call_5.id, literal_9.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=16,
        end_lineno=8,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="b",
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_9.id,
    positional_args=[call_6.id, literal_10.id],
)
