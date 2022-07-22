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
    value="utils",
)
literal_2 = LiteralNode(
    value="__no_imported_submodule",
)
literal_3 = LiteralNode(
    value="save",
)
literal_4 = LiteralNode(
    value="utils",
)
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="getattr",
)
literal_5 = LiteralNode(
    value="lineapy",
)
literal_6 = LiteralNode(
    value="import_data",
)
lookup_6 = LookupNode(
    name="getattr",
)
literal_7 = LiteralNode(
    value="is_prime",
)
lookup_7 = LookupNode(
    name="l_import",
)
literal_8 = LiteralNode(
    value="__no_imported_submodule",
)
lookup_8 = LookupNode(
    name="l_import",
)
source_1 = SourceCode(
    code="""import lineapy
import import_data.utils.__no_imported_submodule
is_prime = import_data.utils.__no_imported_submodule.is_prime

lineapy.save(is_prime, \'is_prime\')
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
    positional_args=[literal_5.id],
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
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    name="import_data.utils.__no_imported_submodule",
    version="",
    package_name="import_data",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_6.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
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
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[literal_8.id, call_3.id],
)
mutate_2 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
mutate_3 = MutateNode(
    source_id=mutate_1.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=11,
        end_lineno=3,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[mutate_3.id, literal_4.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=11,
        end_lineno=3,
        end_col_offset=52,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_5.id, literal_2.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=11,
        end_lineno=3,
        end_col_offset=61,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_6.id, literal_7.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_9 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=23,
        end_lineno=5,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    value="is_prime",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[call_7.id, literal_9.id],
)
