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
    name="l_import",
)
literal_1 = LiteralNode(
    value="Image",
)
literal_2 = LiteralNode(
    value="resize",
)
literal_3 = LiteralNode(
    value="save",
)
lookup_4 = LookupNode(
    name="getattr",
)
lookup_5 = LookupNode(
    name="l_list",
)
lookup_6 = LookupNode(
    name="getattr",
)
lookup_7 = LookupNode(
    name="l_import",
)
literal_4 = LiteralNode(
    value="PIL",
)
lookup_8 = LookupNode(
    name="getattr",
)
literal_5 = LiteralNode(
    value="imsave",
)
literal_6 = LiteralNode(
    value="lineapy",
)
literal_7 = LiteralNode(
    value="pandas",
)
lookup_9 = LookupNode(
    name="file_system",
)
literal_8 = LiteralNode(
    value="pyplot",
)
literal_9 = LiteralNode(
    value="read_csv",
)
lookup_10 = LookupNode(
    name="getattr",
)
lookup_11 = LookupNode(
    name="l_import",
)
lookup_12 = LookupNode(
    name="l_import",
)
literal_10 = LiteralNode(
    value="matplotlib",
)
literal_11 = LiteralNode(
    value="open",
)
lookup_13 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
import matplotlib.pyplot as plt
from PIL.Image import open

df = pd.read_csv(\'tests/simple_data.csv\')
plt.imsave(\'simple_data.png\', df)

img = open(\'simple_data.png\')
img = img.resize([200, 200])

lineapy.save(img, "Graph With Image")
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
    positional_args=[literal_6.id],
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
        end_col_offset=19,
        source_code=source_1.id,
    ),
    function_id=lookup_11.id,
    positional_args=[literal_7.id],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    name="pandas",
    version="",
    package_name="pandas",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_10.id],
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    name="matplotlib.pyplot",
    version="",
    package_name="matplotlib",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    function_id=lookup_12.id,
    positional_args=[literal_8.id, call_3.id],
)
mutate_1 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[literal_4.id],
)
import_4 = ImportNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    name="PIL.Image",
    version="",
    package_name="PIL.Image",
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_1.id, call_5.id],
)
mutate_2 = MutateNode(
    source_id=call_5.id,
    call_id=call_6.id,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_13.id,
    positional_args=[call_6.id, literal_11.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=lookup_10.id,
    positional_args=[call_2.id, literal_9.id],
)
literal_12 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=17,
        end_lineno=6,
        end_col_offset=40,
        source_code=source_1.id,
    ),
    value="tests/simple_data.csv",
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=call_8.id,
    positional_args=[literal_12.id],
    implicit_dependencies=[lookup_9.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_4.id, literal_5.id],
)
literal_13 = LiteralNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=11,
        end_lineno=7,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    value="simple_data.png",
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=33,
        source_code=source_1.id,
    ),
    function_id=call_10.id,
    positional_args=[literal_13.id, call_9.id],
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=11,
        end_lineno=9,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    value="simple_data.png",
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=6,
        end_lineno=9,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    function_id=call_7.id,
    positional_args=[literal_14.id],
    implicit_dependencies=[lookup_9.id],
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=6,
        end_lineno=10,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_12.id, literal_2.id],
)
literal_15 = LiteralNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=18,
        end_lineno=10,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    value=200,
)
literal_16 = LiteralNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=23,
        end_lineno=10,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    value=200,
)
call_14 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=17,
        end_lineno=10,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_15.id, literal_16.id],
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=6,
        end_lineno=10,
        end_col_offset=28,
        source_code=source_1.id,
    ),
    function_id=call_13.id,
    positional_args=[call_14.id],
)
call_16 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_1.id, literal_3.id],
)
literal_17 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=18,
        end_lineno=12,
        end_col_offset=36,
        source_code=source_1.id,
    ),
    value="Graph With Image",
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=37,
        source_code=source_1.id,
    ),
    function_id=call_16.id,
    positional_args=[call_15.id, literal_17.id],
)
