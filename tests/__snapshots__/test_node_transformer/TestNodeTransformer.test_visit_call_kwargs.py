from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.STATIC, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="foo",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 8,
    },
    arguments=[],
    keyword_arguments=[
        (
            "b",
            lineapy_tracer.literal(
                1, {"lineno": 1, "col_offset": 6, "end_lineno": 1, "end_col_offset": 7}
            ),
        )
    ],
)
lineapy_tracer.exit()
