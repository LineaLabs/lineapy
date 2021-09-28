from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.literal(
        0, {"lineno": 1, "col_offset": 4, "end_lineno": 1, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 5,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.lookup_node("a"),
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 5,
    },
)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.literal(
        2, {"lineno": 3, "col_offset": 4, "end_lineno": 3, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 5,
    },
)
lineapy_tracer.exit()
