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
lookup_3 = LookupNode(
    name="pos",
)
lookup_4 = LookupNode(
    name="l_assert",
)
literal_1 = LiteralNode(
    value="decimal",
)
literal_2 = LiteralNode(
    value="Decimal",
)
lookup_5 = LookupNode(
    name="ne",
)
source_1 = SourceCode(
    code="""from decimal import Decimal
obj = Decimal(\'3.1415926535897932384626433832795028841971\')
assert +obj != obj""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_2.id],
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    name="decimal",
    version="",
    package_name="decimal",
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=14,
        end_lineno=2,
        end_col_offset=58,
        source_code=source_1.id,
    ),
    value="3.1415926535897932384626433832795028841971",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=6,
        end_lineno=2,
        end_col_offset=59,
        source_code=source_1.id,
    ),
    function_id=call_2.id,
    positional_args=[literal_3.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=7,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_3.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=7,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_4.id, call_3.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_5.id],
)
