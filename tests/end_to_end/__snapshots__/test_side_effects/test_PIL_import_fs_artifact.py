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
    value="Image",
)
lookup_3 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="lineapy",
)
literal_4 = LiteralNode(
    value="PIL",
)
literal_5 = LiteralNode(
    value="new",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="file_system",
)
literal_6 = LiteralNode(
    value="save",
)
lookup_6 = LookupNode(
    name="l_import",
)
literal_7 = LiteralNode(
    value="open",
)
lookup_7 = LookupNode(
    name="getattr",
)
lookup_8 = LookupNode(
    name="getattr",
)
lookup_9 = LookupNode(
    name="l_tuple",
)
source_1 = SourceCode(
    code="""import lineapy
from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")

lineapy.save(e, \'e\')
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
        end_col_offset=31,
        source_code=source_1.id,
    ),
    name="PIL.Image",
    version="",
    package_name="PIL.Image",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
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
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_1.id, call_2.id],
)
mutate_1 = MutateNode(
    source_id=call_2.id,
    call_id=call_3.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_3.id, literal_5.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_3.id, literal_7.id],
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=14,
        end_lineno=3,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="RGB",
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=22,
        end_lineno=3,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value=4,
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=24,
        end_lineno=3,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    value=4,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=21,
        end_lineno=3,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[literal_9.id, literal_10.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=10,
        end_lineno=3,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=call_4.id,
    positional_args=[literal_8.id, call_6.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_7.id, literal_6.id],
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=13,
        end_lineno=4,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value="test.png",
)
literal_12 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=25,
        end_lineno=4,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    value="PNG",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[literal_11.id, literal_12.id],
)
mutate_2 = MutateNode(
    source_id=lookup_5.id,
    call_id=call_9.id,
)
literal_13 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=9,
        end_lineno=5,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="test.png",
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[literal_13.id],
    implicit_dependencies=[mutate_2.id],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=16,
        end_lineno=7,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="e",
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_11.id,
    positional_args=[call_10.id, literal_14.id],
)
