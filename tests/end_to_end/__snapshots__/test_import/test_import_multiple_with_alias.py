import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=43,
        source_code=source_1.id,
    ),
    library=Library(
        name="math",
    ),
)
call_2 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="pow",
        ).id,
    ],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_2.id,
)
global_2 = GlobalNode(
    name="a",
    call_id=call_2.id,
)
global_3 = GlobalNode(
    name="my_function",
    call_id=call_2.id,
)
global_4 = GlobalNode(
    name="new_df",
    call_id=call_2.id,
)
global_5 = GlobalNode(
    name="r11",
    call_id=call_2.id,
)
global_6 = GlobalNode(
    name="r10",
    call_id=call_2.id,
)
global_7 = GlobalNode(
    name="fn",
    call_id=call_2.id,
)
global_8 = GlobalNode(
    name="new_clf",
    call_id=call_2.id,
)
global_9 = GlobalNode(
    name="X",
    call_id=call_2.id,
)
global_10 = GlobalNode(
    name="DummyClassifier",
    call_id=call_2.id,
)
global_11 = GlobalNode(
    name="sklearn.dummy",
    call_id=call_2.id,
)
global_12 = GlobalNode(
    name="np",
    call_id=call_2.id,
)
global_13 = GlobalNode(
    name="z",
    call_id=call_2.id,
)
global_14 = GlobalNode(
    name="types",
    call_id=call_2.id,
)
global_15 = GlobalNode(
    name="obj",
    call_id=call_2.id,
)
global_16 = GlobalNode(
    name="Decimal",
    call_id=call_2.id,
)
global_17 = GlobalNode(
    name="decimal",
    call_id=call_2.id,
)
global_18 = GlobalNode(
    name="y",
    call_id=call_2.id,
)
global_19 = GlobalNode(
    name="clf",
    call_id=call_2.id,
)
global_20 = GlobalNode(
    name="is_new",
    call_id=call_2.id,
)
global_21 = GlobalNode(
    name="df",
    call_id=call_2.id,
)
global_22 = GlobalNode(
    name="r9",
    call_id=call_2.id,
)
global_23 = GlobalNode(
    name="RandomForestClassifier",
    call_id=call_2.id,
)
global_24 = GlobalNode(
    name="sklearn.ensemble",
    call_id=call_2.id,
)
global_25 = GlobalNode(
    name="sns",
    call_id=call_2.id,
)
global_26 = GlobalNode(
    name="alt",
    call_id=call_2.id,
)
global_27 = GlobalNode(
    name="e",
    call_id=call_2.id,
)
global_28 = GlobalNode(
    name="d",
    call_id=call_2.id,
)
global_29 = GlobalNode(
    name="altair",
    call_id=call_2.id,
)
global_30 = GlobalNode(
    name="r8",
    call_id=call_2.id,
)
global_31 = GlobalNode(
    name="DataFrame",
    call_id=call_2.id,
)
global_32 = GlobalNode(
    name="v",
    call_id=call_2.id,
)
global_33 = GlobalNode(
    name="r7",
    call_id=call_2.id,
)
global_34 = GlobalNode(
    name="r6",
    call_id=call_2.id,
)
global_35 = GlobalNode(
    name="r4",
    call_id=call_2.id,
)
global_36 = GlobalNode(
    name="before",
    call_id=call_2.id,
)
global_37 = GlobalNode(
    name="r5",
    call_id=call_2.id,
)
global_38 = GlobalNode(
    name="r3",
    call_id=call_2.id,
)
global_39 = GlobalNode(
    name="r2",
    call_id=call_2.id,
)
global_40 = GlobalNode(
    name="r1",
    call_id=call_2.id,
)
global_41 = GlobalNode(
    name="assets",
    call_id=call_2.id,
)
global_42 = GlobalNode(
    name="open",
    call_id=call_2.id,
)
global_43 = GlobalNode(
    name="PIL.Image",
    call_id=call_2.id,
)
global_44 = GlobalNode(
    name="plt",
    call_id=call_2.id,
)
global_45 = GlobalNode(
    name="ls",
    call_id=call_2.id,
)
global_46 = GlobalNode(
    name="c",
    call_id=call_2.id,
)
global_47 = GlobalNode(
    name="bs",
    call_id=call_2.id,
)
global_48 = GlobalNode(
    name="pandas",
    call_id=call_2.id,
)
global_49 = GlobalNode(
    name="img",
    call_id=call_2.id,
)
global_50 = GlobalNode(
    name="b",
    call_id=call_2.id,
)
global_51 = GlobalNode(
    name="pd",
    call_id=call_2.id,
)
global_52 = GlobalNode(
    name="x",
    call_id=call_2.id,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="sqrt",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=4,
                end_lineno=2,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            function_id=call_2.id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=10,
                        end_lineno=2,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    value=5,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=13,
                        end_lineno=2,
                        end_col_offset=14,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ],
        ).id
    ],
)
