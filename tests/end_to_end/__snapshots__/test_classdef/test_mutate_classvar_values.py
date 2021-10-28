import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""new_value="newval"
class A():
    def __init__(self, initialname:str):
        self.varname = initialname
    def update_name(newname:str):
        self.varname = newname

class Modifier():
    def modify_A(self,classinstance:A):
        classinstance.varname = new_value

a = A("origvalue")
b = Modifier()
b.modify_A(a)
""",
    location=PosixPath("[source file path]"),
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=14,
        col_offset=0,
        end_lineno=14,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=14,
            col_offset=0,
            end_lineno=14,
            end_col_offset=10,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=13,
                    col_offset=4,
                    end_lineno=13,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                function_id=GlobalNode(
                    name="Modifier",
                    call_id=CallNode(
                        source_location=SourceLocation(
                            lineno=8,
                            col_offset=0,
                            end_lineno=10,
                            end_col_offset=41,
                            source_code=source_1.id,
                        ),
                        function_id=LookupNode(
                            name="l_exec_statement",
                        ).id,
                        positional_args=[
                            LiteralNode(
                                value="""class Modifier():
    def modify_A(self,classinstance:A):
        classinstance.varname = new_value""",
                            ).id
                        ],
                    ).id,
                ).id,
            ).id,
            LiteralNode(
                value="modify_A",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=12,
                col_offset=4,
                end_lineno=12,
                end_col_offset=18,
                source_code=source_1.id,
            ),
            function_id=GlobalNode(
                name="A",
                call_id=CallNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=0,
                        end_lineno=6,
                        end_col_offset=30,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="l_exec_statement",
                    ).id,
                    positional_args=[
                        LiteralNode(
                            value="""class A():
    def __init__(self, initialname:str):
        self.varname = initialname
    def update_name(newname:str):
        self.varname = newname""",
                        ).id
                    ],
                ).id,
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=12,
                        col_offset=6,
                        end_lineno=12,
                        end_col_offset=17,
                        source_code=source_1.id,
                    ),
                    value="origvalue",
                ).id
            ],
        ).id
    ],
    global_reads={
        "new_value": LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=10,
                end_lineno=1,
                end_col_offset=18,
                source_code=source_1.id,
            ),
            value="newval",
        ).id
    },
)
