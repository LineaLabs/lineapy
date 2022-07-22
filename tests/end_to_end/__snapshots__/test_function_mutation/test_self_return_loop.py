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
    name="neg",
)
lookup_4 = LookupNode(
    name="getattr",
)
literal_1 = LiteralNode(
    value="fit",
)
literal_2 = LiteralNode(
    value="save",
)
literal_3 = LiteralNode(
    value="array",
)
literal_4 = LiteralNode(
    value="DummyClassifier",
)
lookup_5 = LookupNode(
    name="l_list",
)
lookup_6 = LookupNode(
    name="getattr",
)
lookup_7 = LookupNode(
    name="getattr",
)
literal_5 = LiteralNode(
    value="lineapy",
)
literal_6 = LiteralNode(
    value="numpy",
)
lookup_8 = LookupNode(
    name="getattr",
)
literal_7 = LiteralNode(
    value="dummy",
)
literal_8 = LiteralNode(
    value="array",
)
literal_9 = LiteralNode(
    value="save",
)
lookup_9 = LookupNode(
    name="getattr",
)
lookup_10 = LookupNode(
    name="l_import",
)
lookup_11 = LookupNode(
    name="l_import",
)
lookup_12 = LookupNode(
    name="l_list",
)
lookup_13 = LookupNode(
    name="getattr",
)
literal_10 = LiteralNode(
    value="fit",
)
literal_11 = LiteralNode(
    value="sklearn",
)
lookup_14 = LookupNode(
    name="getattr",
)
literal_12 = LiteralNode(
    value="fit",
)
lookup_15 = LookupNode(
    name="getattr",
)
source_1 = SourceCode(
    code="""import lineapy
import numpy as np
from sklearn.dummy import DummyClassifier
X = np.array([-1, 1, 1, 1])
y = np.array([0, 1, 1, 1])
clf = DummyClassifier(strategy="most_frequent")
new_clf = clf.fit(X, y)
clf.fit(X, y)
new_clf.fit(X, y)

lineapy.save(new_clf, \'new_clf\')
lineapy.save(clf, \'clf\')
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
        end_col_offset=18,
        source_code=source_1.id,
    ),
    name="numpy",
    version="",
    package_name="numpy",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=lookup_10.id,
    positional_args=[literal_6.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_11.id],
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    name="sklearn.dummy",
    version="",
    package_name="sklearn",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=lookup_11.id,
    positional_args=[literal_7.id, call_3.id],
)
mutate_1 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=lookup_8.id,
    positional_args=[call_4.id, literal_4.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_9.id,
    positional_args=[call_2.id, literal_8.id],
)
literal_13 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=15,
        end_lineno=4,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    value=1,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=14,
        end_lineno=4,
        end_col_offset=16,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_13.id],
)
literal_14 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=18,
        end_lineno=4,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    value=1,
)
literal_15 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=21,
        end_lineno=4,
        end_col_offset=22,
        source_code=source_1.id,
    ),
    value=1,
)
literal_16 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=24,
        end_lineno=4,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    value=1,
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=13,
        end_lineno=4,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=lookup_12.id,
    positional_args=[call_7.id, literal_14.id, literal_15.id, literal_16.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=call_6.id,
    positional_args=[call_8.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[call_2.id, literal_3.id],
)
literal_17 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=14,
        end_lineno=5,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    value=0,
)
literal_18 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=17,
        end_lineno=5,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    value=1,
)
literal_19 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=20,
        end_lineno=5,
        end_col_offset=21,
        source_code=source_1.id,
    ),
    value=1,
)
literal_20 = LiteralNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=23,
        end_lineno=5,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    value=1,
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=13,
        end_lineno=5,
        end_col_offset=25,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_17.id, literal_18.id, literal_19.id, literal_20.id],
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=call_10.id,
    positional_args=[call_11.id],
)
literal_21 = LiteralNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=31,
        end_lineno=6,
        end_col_offset=46,
        source_code=source_1.id,
    ),
    value="most_frequent",
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=6,
        end_lineno=6,
        end_col_offset=47,
        source_code=source_1.id,
    ),
    function_id=call_5.id,
    keyword_args={"strategy": literal_21.id},
)
call_14 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=10,
        end_lineno=7,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_13.id, literal_1.id],
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=10,
        end_lineno=7,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    function_id=call_14.id,
    positional_args=[call_9.id, call_12.id],
)
mutate_2 = MutateNode(
    source_id=call_13.id,
    call_id=call_15.id,
)
call_16 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=lookup_15.id,
    positional_args=[mutate_2.id, literal_12.id],
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=call_16.id,
    positional_args=[call_9.id, call_12.id],
)
mutate_3 = MutateNode(
    source_id=call_15.id,
    call_id=call_17.id,
)
mutate_4 = MutateNode(
    source_id=mutate_2.id,
    call_id=call_17.id,
)
call_18 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_14.id,
    positional_args=[mutate_3.id, literal_10.id],
)
call_19 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=call_18.id,
    positional_args=[call_9.id, call_12.id],
)
mutate_5 = MutateNode(
    source_id=call_17.id,
    call_id=call_19.id,
)
mutate_6 = MutateNode(
    source_id=mutate_3.id,
    call_id=call_19.id,
)
mutate_7 = MutateNode(
    source_id=mutate_4.id,
    call_id=call_19.id,
)
call_20 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_13.id,
    positional_args=[call_1.id, literal_9.id],
)
literal_22 = LiteralNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=22,
        end_lineno=11,
        end_col_offset=31,
        source_code=source_1.id,
    ),
    value="new_clf",
)
call_21 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=0,
        end_lineno=11,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    function_id=call_20.id,
    positional_args=[mutate_6.id, literal_22.id],
)
call_22 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=lookup_7.id,
    positional_args=[call_1.id, literal_2.id],
)
literal_23 = LiteralNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=18,
        end_lineno=12,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    value="clf",
)
call_23 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=0,
        end_lineno=12,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=call_22.id,
    positional_args=[mutate_7.id, literal_23.id],
)
