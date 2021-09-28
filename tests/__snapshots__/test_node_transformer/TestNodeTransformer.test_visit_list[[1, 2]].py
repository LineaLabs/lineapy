from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="__build_list__",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 6,
    },
    arguments=[
        lineapy_tracer.literal(
            1, {"lineno": 1, "col_offset": 1, "end_lineno": 1, "end_col_offset": 2}
        ),
        lineapy_tracer.literal(
            2, {"lineno": 1, "col_offset": 4, "end_lineno": 1, "end_col_offset": 5}
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
