from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.lookup_node("foo"),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 7,
    },
)
lineapy_tracer.exit()
