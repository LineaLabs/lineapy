import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="import types; x = types.SimpleNamespace(); x.hi = 1",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=39,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        ImportNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=12,
                source_code=source_1.id,
            ),
            library=Library(
                name="types",
            ),
        ).id,
        LiteralNode(
            value="SimpleNamespace",
        ).id,
    ],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_1.id,
)
global_2 = GlobalNode(
    name="a",
    call_id=call_1.id,
)
global_3 = GlobalNode(
    name="my_function",
    call_id=call_1.id,
)
global_4 = GlobalNode(
    name="new_df",
    call_id=call_1.id,
)
global_5 = GlobalNode(
    name="r11",
    call_id=call_1.id,
)
global_6 = GlobalNode(
    name="r10",
    call_id=call_1.id,
)
global_7 = GlobalNode(
    name="obj",
    call_id=call_1.id,
)
global_8 = GlobalNode(
    name="Decimal",
    call_id=call_1.id,
)
global_9 = GlobalNode(
    name="decimal",
    call_id=call_1.id,
)
global_10 = GlobalNode(
    name="y",
    call_id=call_1.id,
)
global_11 = GlobalNode(
    name="clf",
    call_id=call_1.id,
)
global_12 = GlobalNode(
    name="is_new",
    call_id=call_1.id,
)
global_13 = GlobalNode(
    name="assets",
    call_id=call_1.id,
)
global_14 = GlobalNode(
    name="RandomForestClassifier",
    call_id=call_1.id,
)
global_15 = GlobalNode(
    name="sklearn.ensemble",
    call_id=call_1.id,
)
global_16 = GlobalNode(
    name="sns",
    call_id=call_1.id,
)
global_17 = GlobalNode(
    name="alt",
    call_id=call_1.id,
)
global_18 = GlobalNode(
    name="e",
    call_id=call_1.id,
)
global_19 = GlobalNode(
    name="d",
    call_id=call_1.id,
)
global_20 = GlobalNode(
    name="altair",
    call_id=call_1.id,
)
global_21 = GlobalNode(
    name="df",
    call_id=call_1.id,
)
global_22 = GlobalNode(
    name="r9",
    call_id=call_1.id,
)
global_23 = GlobalNode(
    name="r8",
    call_id=call_1.id,
)
global_24 = GlobalNode(
    name="r7",
    call_id=call_1.id,
)
global_25 = GlobalNode(
    name="r6",
    call_id=call_1.id,
)
global_26 = GlobalNode(
    name="r5",
    call_id=call_1.id,
)
global_27 = GlobalNode(
    name="DataFrame",
    call_id=call_1.id,
)
global_28 = GlobalNode(
    name="v",
    call_id=call_1.id,
)
global_29 = GlobalNode(
    name="r3",
    call_id=call_1.id,
)
global_30 = GlobalNode(
    name="r2",
    call_id=call_1.id,
)
global_31 = GlobalNode(
    name="r1",
    call_id=call_1.id,
)
global_32 = GlobalNode(
    name="img",
    call_id=call_1.id,
)
global_33 = GlobalNode(
    name="open",
    call_id=call_1.id,
)
global_34 = GlobalNode(
    name="PIL.Image",
    call_id=call_1.id,
)
global_35 = GlobalNode(
    name="plt",
    call_id=call_1.id,
)
global_36 = GlobalNode(
    name="ls",
    call_id=call_1.id,
)
global_37 = GlobalNode(
    name="r4",
    call_id=call_1.id,
)
global_38 = GlobalNode(
    name="c",
    call_id=call_1.id,
)
global_39 = GlobalNode(
    name="math",
    call_id=call_1.id,
)
global_40 = GlobalNode(
    name="bs",
    call_id=call_1.id,
)
global_41 = GlobalNode(
    name="pandas",
    call_id=call_1.id,
)
global_42 = GlobalNode(
    name="x",
    call_id=call_1.id,
)
global_43 = GlobalNode(
    name="pd",
    call_id=call_1.id,
)
global_44 = GlobalNode(
    name="b",
    call_id=call_1.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=43,
        end_lineno=1,
        end_col_offset=51,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="setattr",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=18,
                end_lineno=1,
                end_col_offset=41,
                source_code=source_1.id,
            ),
            function_id=call_1.id,
        ).id,
        LiteralNode(
            value="hi",
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=50,
                end_lineno=1,
                end_col_offset=51,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
    ],
)
