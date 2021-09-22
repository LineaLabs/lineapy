from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.headless_variable(
    "b", {"lineno": 1, "col_offset": 0, "end_lineno": 1, "end_col_offset": 1}
)
lineapy_tracer.exit()
