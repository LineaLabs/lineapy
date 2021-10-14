import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import altair as alt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

import lineapy

alt.data_transformers.enable("json")
alt.renderers.enable("mimetype")

assets = pd.read_csv("tests/ames_train_cleaned.csv")

sns.relplot(data=assets, x="Year_Built", y="SalePrice", size="Lot_Area")


def is_new(col):
    return col > 1970


assets["is_new"] = is_new(assets["Year_Built"])

clf = RandomForestClassifier(random_state=0)
y = assets["is_new"]
x = assets[["SalePrice", "Lot_Area", "Garage_Area"]]

clf.fit(x, y)
p = clf.predict([[100 * 1000, 10, 4]])
lineapy.linea_publish(p, "p value")
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
    library=Library(
        name="altair",
    ),
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=36,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=8,
            col_offset=0,
            end_lineno=8,
            end_col_offset=28,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=8,
                    col_offset=0,
                    end_lineno=8,
                    end_col_offset=21,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    import_1.id,
                    LiteralNode(
                        value="data_transformers",
                    ).id,
                ],
            ).id,
            LiteralNode(
                value="enable",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=8,
                col_offset=29,
                end_lineno=8,
                end_col_offset=35,
                source_code=source_1.id,
            ),
            value="json",
        ).id
    ],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=0,
        end_lineno=9,
        end_col_offset=32,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=9,
            col_offset=0,
            end_lineno=9,
            end_col_offset=20,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=9,
                    col_offset=0,
                    end_lineno=9,
                    end_col_offset=13,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    import_1.id,
                    LiteralNode(
                        value="renderers",
                    ).id,
                ],
            ).id,
            LiteralNode(
                value="enable",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=21,
                end_lineno=9,
                end_col_offset=31,
                source_code=source_1.id,
            ),
            value="mimetype",
        ).id
    ],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=9,
        end_lineno=11,
        end_col_offset=52,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=11,
            col_offset=9,
            end_lineno=11,
            end_col_offset=20,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=0,
                    end_lineno=2,
                    end_col_offset=19,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="pandas",
                ),
            ).id,
            LiteralNode(
                value="read_csv",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=11,
                col_offset=21,
                end_lineno=11,
                end_col_offset=51,
                source_code=source_1.id,
            ),
            value="tests/ames_train_cleaned.csv",
        ).id
    ],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=13,
        col_offset=0,
        end_lineno=13,
        end_col_offset=72,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=13,
            col_offset=0,
            end_lineno=13,
            end_col_offset=11,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=3,
                    end_col_offset=21,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="seaborn",
                ),
            ).id,
            LiteralNode(
                value="relplot",
            ).id,
        ],
    ).id,
    keyword_args={
        "data": call_9.id,
        "size": LiteralNode(
            source_location=SourceLocation(
                lineno=13,
                col_offset=61,
                end_lineno=13,
                end_col_offset=71,
                source_code=source_1.id,
            ),
            value="Lot_Area",
        ).id,
        "x": LiteralNode(
            source_location=SourceLocation(
                lineno=13,
                col_offset=27,
                end_lineno=13,
                end_col_offset=39,
                source_code=source_1.id,
            ),
            value="Year_Built",
        ).id,
        "y": LiteralNode(
            source_location=SourceLocation(
                lineno=13,
                col_offset=43,
                end_lineno=13,
                end_col_offset=54,
                source_code=source_1.id,
            ),
            value="SalePrice",
        ).id,
    },
)
mutate_1 = MutateNode(
    source_id=call_9.id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=20,
            col_offset=0,
            end_lineno=20,
            end_col_offset=47,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="setitem",
        ).id,
        positional_args=[
            call_9.id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=20,
                    col_offset=7,
                    end_lineno=20,
                    end_col_offset=15,
                    source_code=source_1.id,
                ),
                value="is_new",
            ).id,
            CallNode(
                source_location=SourceLocation(
                    lineno=20,
                    col_offset=19,
                    end_lineno=20,
                    end_col_offset=47,
                    source_code=source_1.id,
                ),
                function_id=CallNode(
                    function_id=LookupNode(
                        name="getitem",
                    ).id,
                    positional_args=[
                        CallNode(
                            source_location=SourceLocation(
                                lineno=16,
                                col_offset=0,
                                end_lineno=17,
                                end_col_offset=21,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="__exec__",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    value="""def is_new(col):
    return col > 1970""",
                                ).id,
                                LiteralNode(
                                    value=False,
                                ).id,
                                LiteralNode(
                                    value="is_new",
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            value=0,
                        ).id,
                    ],
                ).id,
                positional_args=[
                    CallNode(
                        source_location=SourceLocation(
                            lineno=20,
                            col_offset=26,
                            end_lineno=20,
                            end_col_offset=46,
                            source_code=source_1.id,
                        ),
                        function_id=LookupNode(
                            name="getitem",
                        ).id,
                        positional_args=[
                            call_9.id,
                            LiteralNode(
                                source_location=SourceLocation(
                                    lineno=20,
                                    col_offset=33,
                                    end_lineno=20,
                                    end_col_offset=45,
                                    source_code=source_1.id,
                                ),
                                value="Year_Built",
                            ).id,
                        ],
                    ).id
                ],
            ).id,
        ],
    ).id,
)
call_17 = CallNode(
    source_location=SourceLocation(
        lineno=22,
        col_offset=6,
        end_lineno=22,
        end_col_offset=44,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
                source_location=SourceLocation(
                    lineno=4,
                    col_offset=0,
                    end_lineno=4,
                    end_col_offset=51,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="sklearn.ensemble",
                ),
            ).id,
            LiteralNode(
                value="RandomForestClassifier",
            ).id,
        ],
    ).id,
    keyword_args={
        "random_state": LiteralNode(
            source_location=SourceLocation(
                lineno=22,
                col_offset=42,
                end_lineno=22,
                end_col_offset=43,
                source_code=source_1.id,
            ),
            value=0,
        ).id
    },
)
call_22 = CallNode(
    source_location=SourceLocation(
        lineno=26,
        col_offset=0,
        end_lineno=26,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=26,
            col_offset=0,
            end_lineno=26,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_17.id,
            LiteralNode(
                value="fit",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=24,
                col_offset=4,
                end_lineno=24,
                end_col_offset=52,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getitem",
            ).id,
            positional_args=[
                mutate_1.id,
                CallNode(
                    source_location=SourceLocation(
                        lineno=24,
                        col_offset=11,
                        end_lineno=24,
                        end_col_offset=51,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="__build_list__",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=24,
                                col_offset=12,
                                end_lineno=24,
                                end_col_offset=23,
                                source_code=source_1.id,
                            ),
                            value="SalePrice",
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=24,
                                col_offset=25,
                                end_lineno=24,
                                end_col_offset=35,
                                source_code=source_1.id,
                            ),
                            value="Lot_Area",
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=24,
                                col_offset=37,
                                end_lineno=24,
                                end_col_offset=50,
                                source_code=source_1.id,
                            ),
                            value="Garage_Area",
                        ).id,
                    ],
                ).id,
            ],
        ).id,
        CallNode(
            source_location=SourceLocation(
                lineno=23,
                col_offset=4,
                end_lineno=23,
                end_col_offset=20,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getitem",
            ).id,
            positional_args=[
                mutate_1.id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=23,
                        col_offset=11,
                        end_lineno=23,
                        end_col_offset=19,
                        source_code=source_1.id,
                    ),
                    value="is_new",
                ).id,
            ],
        ).id,
    ],
)
mutate_3 = MutateNode(
    source_id=call_22.id,
    call_id=call_22.id,
)
call_27 = CallNode(
    source_location=SourceLocation(
        lineno=27,
        col_offset=4,
        end_lineno=27,
        end_col_offset=38,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=27,
            col_offset=4,
            end_lineno=27,
            end_col_offset=15,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            MutateNode(
                source_id=call_17.id,
                call_id=call_22.id,
            ).id,
            LiteralNode(
                value="predict",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=27,
                col_offset=16,
                end_lineno=27,
                end_col_offset=37,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="__build_list__",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=27,
                        col_offset=17,
                        end_lineno=27,
                        end_col_offset=36,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="__build_list__",
                    ).id,
                    positional_args=[
                        CallNode(
                            source_location=SourceLocation(
                                lineno=27,
                                col_offset=18,
                                end_lineno=27,
                                end_col_offset=28,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="mul",
                            ).id,
                            positional_args=[
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=27,
                                        col_offset=18,
                                        end_lineno=27,
                                        end_col_offset=21,
                                        source_code=source_1.id,
                                    ),
                                    value=100,
                                ).id,
                                LiteralNode(
                                    source_location=SourceLocation(
                                        lineno=27,
                                        col_offset=24,
                                        end_lineno=27,
                                        end_col_offset=28,
                                        source_code=source_1.id,
                                    ),
                                    value=1000,
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=27,
                                col_offset=30,
                                end_lineno=27,
                                end_col_offset=32,
                                source_code=source_1.id,
                            ),
                            value=10,
                        ).id,
                        LiteralNode(
                            source_location=SourceLocation(
                                lineno=27,
                                col_offset=34,
                                end_lineno=27,
                                end_col_offset=35,
                                source_code=source_1.id,
                            ),
                            value=4,
                        ).id,
                    ],
                ).id
            ],
        ).id
    ],
)
