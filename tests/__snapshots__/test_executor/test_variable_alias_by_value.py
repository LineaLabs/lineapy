from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.literal(
    assigned_variable_name="a",
    value=0,
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 5,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=Variable("a"),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 5,
    },
)
lineapy_tracer.literal(
    assigned_variable_name="a",
    value=2,
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 5,
    },
)
lineapy_tracer.exit()
