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
lookup_3 = LookupNode(
    name="l_list",
)
source_1 = SourceCode(
    code="""import lineapy
x = []
if True:
    x.append(1)

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
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=True,
)
if_1 = IfNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=3,
        end_lineno=3,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    test_id=literal_3.id,
)
lookup_4 = LookupNode(
    control_dependency=if_1.id,
    name="getattr",
)
literal_4 = LiteralNode(
    control_dependency=if_1.id,
    value="append",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    function_id=lookup_4.id,
    positional_args=[call_2.id, literal_4.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=13,
        end_lineno=4,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    value=1,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    control_dependency=if_1.id,
    function_id=call_3.id,
    positional_args=[literal_5.id],
)
mutate_1 = MutateNode(
    control_dependency=if_1.id,
    source_id=call_2.id,
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
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_1.id],
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=16,
        end_lineno=6,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[mutate_1.id, literal_6.id],
)
