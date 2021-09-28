from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.literal(
        1, {"lineno": 1, "col_offset": 4, "end_lineno": 1, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 5,
    },
)
lineapy_tracer.exit()
