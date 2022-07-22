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
    value="array",
)
lookup_3 = LookupNode(
    name="l_list",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_2 = LiteralNode(
    value="pandas",
)
literal_3 = LiteralNode(
    value="numpy",
)
lookup_5 = LookupNode(
    name="l_import",
)
literal_4 = LiteralNode(
    value="DataFrame",
)
source_1 = SourceCode(
    code="""import pandas, numpy
c = pandas.DataFrame()
d = numpy.array([1,2,3])
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    name="pandas",
    version="",
    package_name="pandas",
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_2.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    name="numpy",
    version="",
    package_name="numpy",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_3.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_4.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    function_id=call_3.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_2.id, literal_1.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=17,
        end_lineno=3,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value=1,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=19,
        end_lineno=3,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    value=2,
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=21,
        end_lineno=3,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    value=3,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=16,
        end_lineno=3,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_5.id, literal_6.id, literal_7.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    positional_args=[call_6.id],
)
