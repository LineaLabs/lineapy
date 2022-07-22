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
    value="save",
)
literal_2 = LiteralNode(
    value="lineapy",
)
literal_3 = LiteralNode(
    value="{1,1,2}",
)
lookup_3 = LookupNode(
    name="l_exec_expr",
)
source_1 = SourceCode(
    code="""import lineapy
x={1,1,2}

lineapy.save(x, \'x\')
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
    name="lineapy",
    version="",
    package_name="lineapy",
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
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=2,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_3.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=16,
        end_lineno=4,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[call_2.id, literal_4.id],
)
