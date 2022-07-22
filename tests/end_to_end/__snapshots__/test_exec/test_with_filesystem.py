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
    value="TemporaryFile",
)
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="file_system",
)
literal_3 = LiteralNode(
    value="lineapy",
)
literal_4 = LiteralNode(
    value="tempfile",
)
lookup_5 = LookupNode(
    name="file_system",
)
literal_5 = LiteralNode(
    value="""with TemporaryFile() as f:
    f.write(b\'some lines\')""",
)
lookup_6 = LookupNode(
    name="l_import",
)
lookup_7 = LookupNode(
    name="l_exec_statement",
)
literal_6 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
from tempfile import TemporaryFile
with TemporaryFile() as f:
    f.write(b\'some lines\')

lineapy.save(lineapy.file_system, \'lineapy.file_system\')
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
    positional_args=[literal_3.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    name="tempfile",
    version="",
    package_name="tempfile",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[literal_4.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_1.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_5.id],
    global_reads={"TemporaryFile": call_3.id},
)
mutate_1 = MutateNode(
    source_id=lookup_5.id,
    call_id=call_4.id,
)
global_1 = GlobalNode(
    name="f",
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_6.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=13,
        end_lineno=6,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
    implicit_dependencies=[mutate_1.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=34,
        end_lineno=6,
        end_col_offset=55,
        source_code=source_1.id,
    ),
    value="lineapy.file_system",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=56,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[call_6.id, literal_7.id],
)
