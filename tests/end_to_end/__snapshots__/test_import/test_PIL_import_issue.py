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
lookup_3 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="open",
)
lookup_4 = LookupNode(
    name="l_tuple",
)
literal_2 = LiteralNode(
    value="PIL",
)
lookup_5 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="Image",
)
lookup_6 = LookupNode(
    name="file_system",
)
literal_4 = LiteralNode(
    value="new",
)
literal_5 = LiteralNode(
    value="save",
)
lookup_7 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id, call_1.id],
)
mutate_1 = MutateNode(
    source_id=call_1.id,
    call_id=call_2.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_2.id, literal_4.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_2.id, literal_1.id],
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    name="PIL.Image",
    version="",
    package_name="PIL.Image",
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=14,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="RGB",
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=22,
        end_lineno=2,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value=4,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=24,
        end_lineno=2,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    value=4,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=21,
        end_lineno=2,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_7.id, literal_8.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=10,
        end_lineno=2,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
    positional_args=[literal_6.id, call_5.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_6.id, literal_5.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=13,
        end_lineno=3,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value="test.png",
)
literal_10 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=25,
        end_lineno=3,
        end_col_offset=30,
        source_code=source_1.id,
    ),
    value="PNG",
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=call_7.id,
    positional_args=[literal_9.id, literal_10.id],
)
mutate_2 = MutateNode(
    source_id=lookup_6.id,
    call_id=call_8.id,
)
literal_11 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=9,
        end_lineno=4,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value="test.png",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=call_4.id,
    positional_args=[literal_11.id],
    implicit_dependencies=[mutate_2.id],
)
