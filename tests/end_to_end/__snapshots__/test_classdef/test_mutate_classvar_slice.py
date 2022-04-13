import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
new_value="newval"
class A():
    def __init__(self, initialname:str):
        self.varname = initialname
    def update_name(newname:str):
        self.varname = newname

class Modifier():
    def modify_A(self,classinstance):
        classinstance.varname = new_value

a = A("origvalue")
b = Modifier()
b.modify_A(a)

lineapy.save(a, \'a\')
lineapy.save(b, \'b\')
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
    version="0.0.1",
    package_name="lineapy",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=13,
        col_offset=4,
        end_lineno=13,
        end_col_offset=18,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="A",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=0,
                end_lineno=7,
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
                lineno=13,
                col_offset=6,
                end_lineno=13,
                end_col_offset=17,
                source_code=source_1.id,
            ),
            value="origvalue",
        ).id
    ],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=14,
        col_offset=4,
        end_lineno=14,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="Modifier",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=9,
                col_offset=0,
                end_lineno=11,
                end_col_offset=41,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_exec_statement",
            ).id,
            positional_args=[
                LiteralNode(
                    value="""class Modifier():
    def modify_A(self,classinstance):
        classinstance.varname = new_value""",
                ).id
            ],
        ).id,
    ).id,
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=15,
        col_offset=0,
        end_lineno=15,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=15,
            col_offset=0,
            end_lineno=15,
            end_col_offset=10,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_4.id,
            LiteralNode(
                value="modify_A",
            ).id,
        ],
    ).id,
    positional_args=[call_3.id],
    global_reads={
        "new_value": LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=10,
                end_lineno=2,
                end_col_offset=18,
                source_code=source_1.id,
            ),
            value="newval",
        ).id
    },
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=17,
        col_offset=0,
        end_lineno=17,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=17,
            col_offset=0,
            end_lineno=17,
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
        call_3.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=17,
                col_offset=16,
                end_lineno=17,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="a",
        ).id,
    ],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=18,
        col_offset=0,
        end_lineno=18,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=18,
            col_offset=0,
            end_lineno=18,
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
        call_4.id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=18,
                col_offset=16,
                end_lineno=18,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value="b",
        ).id,
    ],
)
