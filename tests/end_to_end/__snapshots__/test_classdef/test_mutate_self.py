import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
class Modifier():
    def __init__(self):
        self.varname = None
    def modify_A(self,new_value):
        self.varname = new_value
b = Modifier()
b.modify_A("new")

lineapy.save(b, \'b\')
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="Modifier",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=0,
                end_lineno=6,
                end_col_offset=32,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_exec_statement",
            ).id,
            positional_args=[
                LiteralNode(
                    value="""class Modifier():
    def __init__(self):
        self.varname = None
    def modify_A(self,new_value):
        self.varname = new_value""",
                ).id
            ],
        ).id,
    ).id,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=0,
        end_lineno=10,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=10,
            col_offset=0,
            end_lineno=10,
            end_col_offset=12,
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
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="lineapy",
                ),
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        MutateNode(
            source_id=call_2.id,
            call_id=CallNode(
                source_location=SourceLocation(
                    lineno=8,
                    col_offset=0,
                    end_lineno=8,
                    end_col_offset=17,
                    source_code=source_1.id,
                ),
                function_id=CallNode(
                    source_location=SourceLocation(
                        lineno=8,
                        col_offset=0,
                        end_lineno=8,
                        end_col_offset=10,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="getattr",
                    ).id,
                    positional_args=[
                        call_2.id,
                        LiteralNode(
                            value="modify_A",
                        ).id,
                    ],
                ).id,
                positional_args=[
                    LiteralNode(
                        source_location=SourceLocation(
                            lineno=8,
                            col_offset=11,
                            end_lineno=8,
                            end_col_offset=16,
                            source_code=source_1.id,
                        ),
                        value="new",
                    ).id
                ],
            ).id,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=10,
                col_offset=16,
                end_lineno=10,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="b",
        ).id,
    ],
)
