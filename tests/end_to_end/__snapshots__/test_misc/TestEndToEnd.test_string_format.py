import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="format",
)
source_1 = SourceCode(
    code="a = '{{ {0} }}'.format('foo')",
    location=PosixPath("[source file path]"),
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    value="{{ {0} }}",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id, literal_1.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=23,
        end_lineno=1,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    value="foo",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=call_1.id,
    positional_args=[literal_3.id],
)
