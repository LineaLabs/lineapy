import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

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

lineapy.linea_publish(new_clf, \'new_clf\')
lineapy.linea_publish(clf, \'clf\')
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    library=Library(
        name="numpy",
    ),
)
call_1 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        ImportNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=0,
                end_lineno=3,
                end_col_offset=41,
                source_code=source_1.id,
            ),
            library=Library(
                name="sklearn.dummy",
            ),
        ).id,
        LiteralNode(
            value="DummyClassifier",
        ).id,
    ],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_1.id,
)
global_2 = GlobalNode(
    name="x",
    call_id=call_1.id,
)
global_3 = GlobalNode(
    name="v",
    call_id=call_1.id,
)
global_4 = GlobalNode(
    name="new_df",
    call_id=call_1.id,
)
global_5 = GlobalNode(
    name="pd",
    call_id=call_1.id,
)
global_6 = GlobalNode(
    name="before",
    call_id=call_1.id,
)
global_7 = GlobalNode(
    name="types",
    call_id=call_1.id,
)
global_8 = GlobalNode(
    name="Decimal",
    call_id=call_1.id,
)
global_9 = GlobalNode(
    name="obj",
    call_id=call_1.id,
)
global_10 = GlobalNode(
    name="df",
    call_id=call_1.id,
)
global_11 = GlobalNode(
    name="y",
    call_id=call_1.id,
)
global_12 = GlobalNode(
    name="decimal",
    call_id=call_1.id,
)
global_13 = GlobalNode(
    name="is_new",
    call_id=call_1.id,
)
global_14 = GlobalNode(
    name="clf",
    call_id=call_1.id,
)
global_15 = GlobalNode(
    name="assets",
    call_id=call_1.id,
)
global_16 = GlobalNode(
    name="RandomForestClassifier",
    call_id=call_1.id,
)
global_17 = GlobalNode(
    name="sklearn.ensemble",
    call_id=call_1.id,
)
global_18 = GlobalNode(
    name="alt",
    call_id=call_1.id,
)
global_19 = GlobalNode(
    name="bs",
    call_id=call_1.id,
)
global_20 = GlobalNode(
    name="pandas",
    call_id=call_1.id,
)
global_21 = GlobalNode(
    name="DataFrame",
    call_id=call_1.id,
)
global_22 = GlobalNode(
    name="sns",
    call_id=call_1.id,
)
global_23 = GlobalNode(
    name="ls",
    call_id=call_1.id,
)
global_24 = GlobalNode(
    name="r11",
    call_id=call_1.id,
)
global_25 = GlobalNode(
    name="r10",
    call_id=call_1.id,
)
global_26 = GlobalNode(
    name="altair",
    call_id=call_1.id,
)
global_27 = GlobalNode(
    name="e",
    call_id=call_1.id,
)
global_28 = GlobalNode(
    name="r8",
    call_id=call_1.id,
)
global_29 = GlobalNode(
    name="d",
    call_id=call_1.id,
)
global_30 = GlobalNode(
    name="r6",
    call_id=call_1.id,
)
global_31 = GlobalNode(
    name="r4",
    call_id=call_1.id,
)
global_32 = GlobalNode(
    name="c",
    call_id=call_1.id,
)
global_33 = GlobalNode(
    name="math",
    call_id=call_1.id,
)
global_34 = GlobalNode(
    name="my_function",
    call_id=call_1.id,
)
global_35 = GlobalNode(
    name="b",
    call_id=call_1.id,
)
global_36 = GlobalNode(
    name="img",
    call_id=call_1.id,
)
global_37 = GlobalNode(
    name="r9",
    call_id=call_1.id,
)
global_38 = GlobalNode(
    name="a",
    call_id=call_1.id,
)
global_39 = GlobalNode(
    name="r7",
    call_id=call_1.id,
)
global_40 = GlobalNode(
    name="r5",
    call_id=call_1.id,
)
global_41 = GlobalNode(
    name="plt",
    call_id=call_1.id,
)
global_42 = GlobalNode(
    name="r1",
    call_id=call_1.id,
)
global_43 = GlobalNode(
    name="r3",
    call_id=call_1.id,
)
global_44 = GlobalNode(
    name="r2",
    call_id=call_1.id,
)
global_45 = GlobalNode(
    name="PIL.Image",
    call_id=call_1.id,
)
global_46 = GlobalNode(
    name="open",
    call_id=call_1.id,
)
global_47 = GlobalNode(
    name="z",
    call_id=call_1.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=27,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=4,
            col_offset=4,
            end_lineno=4,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="array",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=13,
                end_lineno=4,
                end_col_offset=26,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=14,
                        end_lineno=4,
                        end_col_offset=16,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="neg",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=15,
                                end_lineno=4,
                                end_col_offset=16,
                                source_code=source_1.id,
                            ),
                            value=1,
                        ).id
                    ],
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=18,
                        end_lineno=4,
                        end_col_offset=19,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=21,
                        end_lineno=4,
                        end_col_offset=22,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=24,
                        end_lineno=4,
                        end_col_offset=25,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
            ],
        ).id
    ],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=26,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=4,
            end_lineno=5,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="array",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=13,
                end_lineno=5,
                end_col_offset=25,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=14,
                        end_lineno=5,
                        end_col_offset=15,
                        source_code=source_1.id,
                    ),
                    value=0,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=17,
                        end_lineno=5,
                        end_col_offset=18,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=20,
                        end_lineno=5,
                        end_col_offset=21,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=23,
                        end_lineno=5,
                        end_col_offset=24,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
            ],
        ).id
    ],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=6,
        end_lineno=6,
        end_col_offset=47,
        source_code=source_1.id,
    ),
    function_id=call_1.id,
    keyword_args={
        "strategy": LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=31,
                end_lineno=6,
                end_col_offset=46,
                source_code=source_1.id,
            ),
            value="most_frequent",
        ).id
    },
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=10,
        end_lineno=7,
        end_col_offset=23,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=10,
            end_lineno=7,
            end_col_offset=17,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_9.id,
            LiteralNode(
                value="fit",
            ).id,
        ],
    ).id,
    positional_args=[call_5.id, call_8.id],
)
mutate_1 = MutateNode(
    source_id=call_9.id,
    call_id=call_11.id,
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=8,
            col_offset=0,
            end_lineno=8,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            mutate_1.id,
            LiteralNode(
                value="fit",
            ).id,
        ],
    ).id,
    positional_args=[call_5.id, call_8.id],
)
mutate_2 = MutateNode(
    source_id=call_11.id,
    call_id=call_13.id,
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=9,
            col_offset=0,
            end_lineno=9,
            end_col_offset=11,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            mutate_2.id,
            LiteralNode(
                value="fit",
            ).id,
        ],
    ).id,
    positional_args=[call_5.id, call_8.id],
)
mutate_5 = MutateNode(
    source_id=call_13.id,
    call_id=call_15.id,
)
mutate_9 = MutateNode(
    source_id=MutateNode(
        source_id=mutate_2.id,
        call_id=call_15.id,
    ).id,
    call_id=call_15.id,
)
mutate_11 = MutateNode(
    source_id=MutateNode(
        source_id=MutateNode(
            source_id=MutateNode(
                source_id=MutateNode(
                    source_id=MutateNode(
                        source_id=mutate_1.id,
                        call_id=call_13.id,
                    ).id,
                    call_id=call_13.id,
                ).id,
                call_id=call_15.id,
            ).id,
            call_id=call_15.id,
        ).id,
        call_id=call_15.id,
    ).id,
    call_id=call_15.id,
)
