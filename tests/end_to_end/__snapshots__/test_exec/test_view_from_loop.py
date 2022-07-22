import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_exec_statement",
)
literal_1 = LiteralNode(
    value="""for x in xs:
    pass""",
)
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="lineapy",
)
lookup_5 = LookupNode(
    name="l_list",
)
literal_4 = LiteralNode(
    value="append",
)
lookup_6 = LookupNode(
    name="l_list",
)
lookup_7 = LookupNode(
    name="getattr",
)
literal_5 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
xs = [[]]
for x in xs:
    pass
x.append(10)

lineapy.save(x, \'x\')
lineapy.save(xs, \'xs\')
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
        col_offset=6,
        end_lineno=2,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=5,
        end_lineno=2,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_2.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_1.id],
    global_reads={"xs": call_3.id},
)
global_1 = GlobalNode(
    name="x",
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[global_1.id, literal_4.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=9,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    value=10,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[literal_6.id],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_6.id,
)
mutate_2 = MutateNode(
    source_id=call_3.id,
    call_id=call_6.id,
)
mutate_3 = MutateNode(
    source_id=global_1.id,
    call_id=call_6.id,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=16,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
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
    positional_args=[mutate_3.id, literal_7.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_5.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=17,
        end_lineno=8,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    value="xs",
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=call_9.id,
    positional_args=[mutate_2.id, literal_8.id],
)
