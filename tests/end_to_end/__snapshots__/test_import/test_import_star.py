import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""from math import *
mypi = pi
x = sqrt(4)
""",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    library=Library(
        name="math",
    ),
)
call_1 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="atan2",
        ).id,
    ],
)
call_2 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="cos",
        ).id,
    ],
)
call_3 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="fmod",
        ).id,
    ],
)
call_4 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="exp",
        ).id,
    ],
)
call_5 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="ulp",
        ).id,
    ],
)
call_6 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="radians",
        ).id,
    ],
)
call_7 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="isinf",
        ).id,
    ],
)
call_8 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="tanh",
        ).id,
    ],
)
call_9 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="asinh",
        ).id,
    ],
)
call_10 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="sin",
        ).id,
    ],
)
call_11 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="lcm",
        ).id,
    ],
)
call_12 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="nextafter",
        ).id,
    ],
)
call_13 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="tau",
        ).id,
    ],
)
call_14 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="atan",
        ).id,
    ],
)
call_15 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="log2",
        ).id,
    ],
)
call_16 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="log",
        ).id,
    ],
)
call_17 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="fabs",
        ).id,
    ],
)
call_18 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="floor",
        ).id,
    ],
)
call_19 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="ldexp",
        ).id,
    ],
)
call_20 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="degrees",
        ).id,
    ],
)
call_21 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="modf",
        ).id,
    ],
)
call_22 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="log1p",
        ).id,
    ],
)
call_23 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="frexp",
        ).id,
    ],
)
call_24 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="acos",
        ).id,
    ],
)
call_25 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="gamma",
        ).id,
    ],
)
call_26 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="nan",
        ).id,
    ],
)
call_27 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="hypot",
        ).id,
    ],
)
call_28 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="factorial",
        ).id,
    ],
)
call_29 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="isqrt",
        ).id,
    ],
)
call_30 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="erfc",
        ).id,
    ],
)
call_31 = CallNode(
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
call_32 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="tan",
        ).id,
    ],
)
call_33 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="atanh",
        ).id,
    ],
)
call_34 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="e",
        ).id,
    ],
)
call_35 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="erf",
        ).id,
    ],
)
call_37 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="lgamma",
        ).id,
    ],
)
call_38 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="cosh",
        ).id,
    ],
)
call_39 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="expm1",
        ).id,
    ],
)
call_40 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="prod",
        ).id,
    ],
)
call_41 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="trunc",
        ).id,
    ],
)
call_42 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="inf",
        ).id,
    ],
)
call_43 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="pi",
        ).id,
    ],
)
call_44 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="isfinite",
        ).id,
    ],
)
call_45 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="isnan",
        ).id,
    ],
)
call_46 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="isclose",
        ).id,
    ],
)
call_47 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="sinh",
        ).id,
    ],
)
call_48 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="perm",
        ).id,
    ],
)
call_49 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="asin",
        ).id,
    ],
)
call_50 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="gcd",
        ).id,
    ],
)
call_51 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="dist",
        ).id,
    ],
)
call_52 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="log10",
        ).id,
    ],
)
call_53 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="comb",
        ).id,
    ],
)
call_54 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="acosh",
        ).id,
    ],
)
call_55 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="copysign",
        ).id,
    ],
)
call_56 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="ceil",
        ).id,
    ],
)
call_57 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="fsum",
        ).id,
    ],
)
call_58 = CallNode(
    function_id=LookupNode(
        name="getattr",
    ).id,
    positional_args=[
        import_1.id,
        LiteralNode(
            value="remainder",
        ).id,
    ],
)
call_59 = CallNode(
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
        LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=9,
                end_lineno=3,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=4,
        ).id
    ],
)
