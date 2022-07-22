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
lookup_3 = LookupNode(
    name="getattr",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="save",
)
lookup_5 = LookupNode(
    name="getattr",
)
literal_3 = LiteralNode(
    value="save",
)
literal_4 = LiteralNode(
    value="__no_imported_submodule_prime",
)
lookup_6 = LookupNode(
    name="getattr",
)
literal_5 = LiteralNode(
    value="__no_imported_submodule_prime",
)
literal_6 = LiteralNode(
    value="is_prime",
)
literal_7 = LiteralNode(
    value="lineapy",
)
literal_8 = LiteralNode(
    value="import_data",
)
lookup_7 = LookupNode(
    name="l_import",
)
literal_9 = LiteralNode(
    value="utils",
)
lookup_8 = LookupNode(
    name="getattr",
)
lookup_9 = LookupNode(
    name="getattr",
)
lookup_10 = LookupNode(
    name="getattr",
)
lookup_11 = LookupNode(
    name="l_import",
)
literal_10 = LiteralNode(
    value="__no_imported_submodule",
)
literal_11 = LiteralNode(
    value="is_prime",
)
literal_12 = LiteralNode(
    value="__no_imported_submodule",
)
lookup_12 = LookupNode(
    name="l_import",
)
literal_13 = LiteralNode(
    value="utils",
)
lookup_13 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
import import_data.utils.__no_imported_submodule
import import_data.utils.__no_imported_submodule_prime
first_is_prime = import_data.utils.__no_imported_submodule.is_prime
second_is_prime = import_data.utils.__no_imported_submodule_prime.is_prime

lineapy.save(first_is_prime, \'first_is_prime\')
lineapy.save(second_is_prime, \'second_is_prime\')
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
    positional_args=[literal_7.id],
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
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=lookup_11.id,
    positional_args=[literal_8.id],
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
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=lookup_12.id,
    positional_args=[literal_10.id, call_3.id],
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
        col_offset=0,
        end_lineno=3,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_4.id, mutate_2.id],
)
mutate_4 = MutateNode(
    source_id=call_4.id,
    call_id=call_5.id,
)
mutate_5 = MutateNode(
    source_id=mutate_2.id,
    call_id=call_5.id,
)
mutate_6 = MutateNode(
    source_id=mutate_3.id,
    call_id=call_5.id,
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    name="import_data.utils.__no_imported_submodule_prime",
    version="",
    package_name="import_data",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=17,
        end_lineno=4,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=lookup_13.id,
    positional_args=[mutate_6.id, literal_13.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=17,
        end_lineno=4,
        end_col_offset=58,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_6.id, literal_12.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=17,
        end_lineno=4,
        end_col_offset=67,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[call_7.id, literal_11.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=18,
        end_lineno=5,
        end_col_offset=35,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[mutate_6.id, literal_9.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=18,
        end_lineno=5,
        end_col_offset=65,
        source_code=source_1.id,
    ),
    function_id=lookup_10.id,
    positional_args=[call_9.id, literal_5.id],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=18,
        end_lineno=5,
        end_col_offset=74,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[call_10.id, literal_6.id],
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=29,
        end_lineno=7,
        end_col_offset=45,
        source_code=source_1.id,
    ),
    value="first_is_prime",
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=46,
        source_code=source_1.id,
    ),
    function_id=call_12.id,
    positional_args=[call_8.id, literal_14.id],
)
call_14 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_15 = LiteralNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=30,
        end_lineno=8,
        end_col_offset=47,
        source_code=source_1.id,
    ),
    value="second_is_prime",
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=call_14.id,
    positional_args=[call_11.id, literal_15.id],
)
