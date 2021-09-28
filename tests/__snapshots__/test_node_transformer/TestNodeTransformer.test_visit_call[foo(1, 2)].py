from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.STATIC, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="foo",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 9,
    },
    arguments=[
        lineapy_tracer.literal(
            1, {"lineno": 1, "col_offset": 4, "end_lineno": 1, "end_col_offset": 5}
        ),
        lineapy_tracer.literal(
            2, {"lineno": 1, "col_offset": 7, "end_lineno": 1, "end_col_offset": 8}
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
