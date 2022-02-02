import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import lineapy.utils.__no_imported_submodule
import lineapy.utils
is_prime = lineapy.utils.__no_imported_submodule.is_prime

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
    library=Library(
        name="lineapy",
    ),
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=44,
        source_code=source_1.id,
    ),
    library=Library(
        name="lineapy.utils.__no_imported_submodule",
    ),
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    library=Library(
        name="lineapy.utils",
    ),
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=0,
        end_lineno=6,
        end_col_offset=34,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=6,
            col_offset=0,
            end_lineno=6,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            import_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=11,
                end_lineno=4,
                end_col_offset=57,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=11,
                        end_lineno=4,
                        end_col_offset=48,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="getattr",
                    ).id,
                    positional_args=[
                        CallNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=11,
                                end_lineno=4,
                                end_col_offset=24,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                import_1.id,
                                LiteralNode(
                                    value="utils",
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            value="__no_imported_submodule",
                        ).id,
                    ],
                ).id,
                LiteralNode(
                    value="is_prime",
                ).id,
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=23,
                end_lineno=6,
                end_col_offset=33,
                source_code=source_1.id,
            ),
            value="is_prime",
        ).id,
    ],
)
