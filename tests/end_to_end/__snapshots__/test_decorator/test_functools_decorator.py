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
    value="lru_cache",
)
literal_2 = LiteralNode(
    value="save",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="lineapy",
)
literal_4 = LiteralNode(
    value="functools",
)
literal_5 = LiteralNode(
    value="""@lru_cache(maxsize=1)
def f():
    return 1""",
)
lookup_4 = LookupNode(
    name="l_import",
)
lookup_5 = LookupNode(
    name="l_exec_statement",
)
source_1 = SourceCode(
    code="""import lineapy
from functools import lru_cache
@lru_cache(maxsize=1)
def f():
    return 1

x = f()

lineapy.save(x, \'x\')
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
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_4.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    name="functools",
    version="",
    package_name="functools",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_2.id, literal_1.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_5.id],
    global_reads={"lru_cache": call_3.id},
)
global_1 = GlobalNode(
    name="f",
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=16,
        end_lineno=9,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[call_5.id, literal_6.id],
)
