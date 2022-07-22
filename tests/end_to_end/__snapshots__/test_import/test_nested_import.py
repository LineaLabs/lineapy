import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_import",
)
lookup_2 = LookupNode(
    name="l_import",
)
literal_1 = LiteralNode(
    value="pyplot",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="pyplot",
)
literal_3 = LiteralNode(
    value="ylabel",
)
literal_4 = LiteralNode(
    value="lineapy",
)
literal_5 = LiteralNode(
    value="matplotlib",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="getattr",
)
lookup_6 = LookupNode(
    name="l_import",
)
literal_6 = LiteralNode(
    value="save",
)
source_1 = SourceCode(
    code="""import lineapy
import matplotlib.pyplot
x = matplotlib.pyplot.ylabel(\'label\')

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
    positional_args=[literal_4.id],
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
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[literal_5.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_1.id, call_2.id],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_3.id,
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    name="matplotlib.pyplot",
    version="",
    package_name="matplotlib",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[mutate_1.id, literal_2.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_4.id, literal_3.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=29,
        end_lineno=3,
        end_col_offset=36,
        source_code=source_1.id,
    ),
    value="label",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=37,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[literal_7.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_6.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=16,
        end_lineno=5,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="x",
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_7.id,
    positional_args=[call_6.id, literal_8.id],
)
