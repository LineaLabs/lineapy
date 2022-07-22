import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
from import_data.utils import __no_imported_submodule
is_prime = __no_imported_submodule.is_prime

lineapy.save(is_prime, \'is_prime\')
""",
    location=PosixPath("[source file path]"),
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
        end_col_offset=53,
        source_code=source_1.id,
    ),
    name="import_data.utils",
    version="",
    package_name="import_data",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=53,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="import_data",
        ).id
    ],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=53,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="utils",
        ).id,
        call_2.id,
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=53,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="__no_imported_submodule",
        ).id,
        call_3.id,
    ],
)
mutate_2 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
mutate_3 = MutateNode(
    source_id=MutateNode(
        source_id=call_2.id,
        call_id=call_3.id,
    ).id,
    call_id=call_4.id,
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=0,
        end_lineno=5,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=5,
            col_offset=0,
            end_lineno=5,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_import",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="lineapy",
                    ).id
                ],
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=11,
                end_lineno=3,
                end_col_offset=43,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                call_4.id,
                LiteralNode(
                    value="is_prime",
                ).id,
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=23,
                end_lineno=5,
                end_col_offset=33,
                source_code=source_1.id,
            ),
            value="is_prime",
        ).id,
    ],
)
