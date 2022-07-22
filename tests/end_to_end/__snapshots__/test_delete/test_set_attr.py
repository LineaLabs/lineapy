import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="setattr",
)
literal_1 = LiteralNode(
    value="hi",
)
literal_2 = LiteralNode(
    value="types",
)
literal_3 = LiteralNode(
    value="SimpleNamespace",
)
lookup_3 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="import types; x = types.SimpleNamespace(); x.hi = 1",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    name="types",
    version="",
    package_name="types",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=39,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_3.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=call_2.id,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=50,
        end_lineno=1,
        end_col_offset=51,
        source_code=source_1.id,
    ),
    value=1,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=43,
        end_lineno=1,
        end_col_offset=51,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_3.id, literal_1.id, literal_4.id],
)
mutate_1 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
