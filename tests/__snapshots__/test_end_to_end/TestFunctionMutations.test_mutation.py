import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
x = {}
x[\'a\'] = 3

lineapy.linea_publish(x, \'x\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_dict",
    ).id,
)
mutate_1 = MutateNode(
    source_id=call_1.id,
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=0,
            end_lineno=3,
            end_col_offset=10,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="setitem",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=2,
                    end_lineno=3,
                    end_col_offset=5,
                    source_code=source_1.id,
                ),
                value="a",
            ).id,
            LiteralNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=9,
                    end_lineno=3,
                    end_col_offset=10,
                    source_code=source_1.id,
                ),
                value=3,
            ).id,
        ],
    ).id,
)
