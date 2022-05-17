import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="import types; x = types.SimpleNamespace(); x.hi = 1; del x.hi",
    location=PosixPath("[source file path]"),
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    name="types",
    version="",
    package_name="types",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=18,
        end_lineno=1,
        end_col_offset=41,
        source_code=source_1.id,
    ),
    function_id=CallNode(
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
            CallNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=12,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_import",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="types",
                    ).id
                ],
            ).id,
            LiteralNode(
                value="SimpleNamespace",
            ).id,
        ],
    ).id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=53,
        end_lineno=1,
        end_col_offset=61,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="delattr",
    ).id,
    positional_args=[
        MutateNode(
            source_id=call_3.id,
            call_id=CallNode(
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
                    call_3.id,
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
            ).id,
        ).id,
        LiteralNode(
            value="hi",
        ).id,
    ],
)
