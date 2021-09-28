from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="getitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 5,
    },
    arguments=[
        lineapy_tracer.lookup_node("ls"),
        lineapy_tracer.literal(
            0, {"lineno": 1, "col_offset": 3, "end_lineno": 1, "end_col_offset": 4}
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
