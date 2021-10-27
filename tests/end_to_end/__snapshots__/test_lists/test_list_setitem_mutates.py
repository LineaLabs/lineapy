import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = []
x.append(10)

lineapy.linea_publish(x, \'x\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_list",
    ).id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=0,
            end_lineno=3,
            end_col_offset=8,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value="append",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=9,
                end_lineno=3,
                end_col_offset=11,
                source_code=source_1.id,
            ),
            value=10,
        ).id
    ],
)
mutate_1 = MutateNode(
    source_id=GlobalNode(
        name="v",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_2 = MutateNode(
    source_id=GlobalNode(
        name="pandas",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_3 = MutateNode(
    source_id=GlobalNode(
        name="r11",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_4 = MutateNode(
    source_id=GlobalNode(
        name="assets",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_5 = MutateNode(
    source_id=GlobalNode(
        name="c",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_6 = MutateNode(
    source_id=GlobalNode(
        name="cubed",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_7 = MutateNode(
    source_id=GlobalNode(
        name="my_function",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_8 = MutateNode(
    source_id=GlobalNode(
        name="d",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_9 = MutateNode(
    source_id=GlobalNode(
        name="new_img",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_10 = MutateNode(
    source_id=GlobalNode(
        name="x",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_11 = MutateNode(
    source_id=GlobalNode(
        name="X",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_12 = MutateNode(
    source_id=GlobalNode(
        name="e",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_13 = MutateNode(
    source_id=GlobalNode(
        name="types",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_14 = MutateNode(
    source_id=GlobalNode(
        name="a",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_15 = MutateNode(
    source_id=GlobalNode(
        name="DataFrame",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_16 = MutateNode(
    source_id=GlobalNode(
        name="alt",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_17 = MutateNode(
    source_id=GlobalNode(
        name="DummyClassifier",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_18 = MutateNode(
    source_id=GlobalNode(
        name="z",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_19 = MutateNode(
    source_id=GlobalNode(
        name="plt",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_20 = MutateNode(
    source_id=GlobalNode(
        name="sns",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_21 = MutateNode(
    source_id=GlobalNode(
        name="ls",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_22 = MutateNode(
    source_id=GlobalNode(
        name="Decimal",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_23 = MutateNode(
    source_id=GlobalNode(
        name="new",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_24 = MutateNode(
    source_id=GlobalNode(
        name="r5",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_25 = MutateNode(
    source_id=GlobalNode(
        name="decimal",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_26 = MutateNode(
    source_id=GlobalNode(
        name="obj",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_27 = MutateNode(
    source_id=GlobalNode(
        name="r8",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_28 = MutateNode(
    source_id=GlobalNode(
        name="y",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_29 = MutateNode(
    source_id=call_1.id,
    call_id=call_3.id,
)
mutate_30 = MutateNode(
    source_id=GlobalNode(
        name="before",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_31 = MutateNode(
    source_id=GlobalNode(
        name="b",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_32 = MutateNode(
    source_id=GlobalNode(
        name="sklearn.dummy",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_33 = MutateNode(
    source_id=GlobalNode(
        name="root",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_34 = MutateNode(
    source_id=GlobalNode(
        name="fn",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_35 = MutateNode(
    source_id=GlobalNode(
        name="new_clf",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_36 = MutateNode(
    source_id=GlobalNode(
        name="math",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_37 = MutateNode(
    source_id=GlobalNode(
        name="power",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_38 = MutateNode(
    source_id=GlobalNode(
        name="is_new",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_39 = MutateNode(
    source_id=GlobalNode(
        name="new_df",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_40 = MutateNode(
    source_id=GlobalNode(
        name="r3",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_41 = MutateNode(
    source_id=GlobalNode(
        name="r9",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_42 = MutateNode(
    source_id=GlobalNode(
        name="numpy",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_43 = MutateNode(
    source_id=GlobalNode(
        name="RandomForestClassifier",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_44 = MutateNode(
    source_id=GlobalNode(
        name="clf",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_45 = MutateNode(
    source_id=GlobalNode(
        name="open",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_46 = MutateNode(
    source_id=GlobalNode(
        name="list_1",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_47 = MutateNode(
    source_id=GlobalNode(
        name="img",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_48 = MutateNode(
    source_id=GlobalNode(
        name="r1",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_49 = MutateNode(
    source_id=GlobalNode(
        name="r2",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_50 = MutateNode(
    source_id=GlobalNode(
        name="sum_call_list",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_51 = MutateNode(
    source_id=GlobalNode(
        name="sklearn.ensemble",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_52 = MutateNode(
    source_id=GlobalNode(
        name="altair",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_53 = MutateNode(
    source_id=GlobalNode(
        name="pd",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_54 = MutateNode(
    source_id=GlobalNode(
        name="r7",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_55 = MutateNode(
    source_id=GlobalNode(
        name="foo",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_56 = MutateNode(
    source_id=GlobalNode(
        name="r4",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_57 = MutateNode(
    source_id=GlobalNode(
        name="r10",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_58 = MutateNode(
    source_id=GlobalNode(
        name="np",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_59 = MutateNode(
    source_id=GlobalNode(
        name="PIL.Image",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_60 = MutateNode(
    source_id=GlobalNode(
        name="r6",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_61 = MutateNode(
    source_id=GlobalNode(
        name="df",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_62 = MutateNode(
    source_id=GlobalNode(
        name="bs",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
