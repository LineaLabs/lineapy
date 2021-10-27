import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
def foo():
    def inner():
        return 1
    return inner
c = foo()()

lineapy.save(c, \'c\')
""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=6,
            col_offset=4,
            end_lineno=6,
            end_col_offset=9,
            source_code=source_1.id,
        ),
        function_id=GlobalNode(
            name="foo",
            call_id=CallNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=0,
                    end_lineno=5,
                    end_col_offset=16,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="l_exec_statement",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""def foo():
    def inner():
        return 1
    return inner""",
                    ).id
                ],
            ).id,
        ).id,
    ).id,
)
