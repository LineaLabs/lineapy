import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
literal_1 = LiteralNode(
    value="""def append1(func):
    def wrapper():
        func()
        x.append(1)

    return wrapper""",
)
lookup_2 = LookupNode(
    name="l_exec_statement",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="lineapy",
)
lookup_3 = LookupNode(
    name="l_exec_statement",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="l_list",
)
literal_4 = LiteralNode(
    value="""@append1
def append2():
    x.append(2)""",
)
source_1 = SourceCode(
    code="""import lineapy
x=[]
def append1(func):
    def wrapper():
        func()
        x.append(1)

    return wrapper


@append1
def append2():
    x.append(2)

append2()

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
        col_offset=2,
        end_lineno=2,
        end_col_offset=4,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=8,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_1.id],
)
global_1 = GlobalNode(
    name="append1",
    call_id=call_3.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=13,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_4.id],
    global_reads={"append1": global_1.id},
)
global_2 = GlobalNode(
    name="append2",
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=15,
        col_offset=0,
        end_lineno=15,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=global_2.id,
    global_reads={"x": call_2.id},
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_5.id,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=17,
        col_offset=0,
        end_lineno=17,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=17,
        col_offset=16,
        end_lineno=17,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=17,
        col_offset=0,
        end_lineno=17,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[mutate_1.id, literal_5.id],
)
