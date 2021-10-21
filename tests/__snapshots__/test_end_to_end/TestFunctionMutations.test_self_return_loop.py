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
                name="__build_list__",
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
                name="__build_list__",
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
    function_id=CallNode(
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
    ).id,
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
mutate_4 = MutateNode(
    source_id=mutate_1.id,
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
    source_id=mutate_2.id,
    call_id=call_15.id,
)
mutate_6 = MutateNode(
    source_id=mutate_4.id,
    call_id=call_15.id,
)
mutate_7 = MutateNode(
    source_id=mutate_4.id,
    call_id=call_15.id,
)
mutate_8 = MutateNode(
    source_id=call_13.id,
    call_id=call_15.id,
)
mutate_9 = MutateNode(
    source_id=MutateNode(
        source_id=mutate_1.id,
        call_id=call_13.id,
    ).id,
    call_id=call_15.id,
)
mutate_10 = MutateNode(
    source_id=mutate_4.id,
    call_id=call_15.id,
)
mutate_11 = MutateNode(
    source_id=mutate_2.id,
    call_id=call_15.id,
)
