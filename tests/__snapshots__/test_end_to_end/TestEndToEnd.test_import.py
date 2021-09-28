from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="math",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 43,
    },
    attributes={"power": "pow", "root": "sqrt"},
)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.call(
        function_name="power",
        syntax_dictionary={
            "lineno": 2,
            "col_offset": 4,
            "end_lineno": 2,
            "end_col_offset": 15,
        },
        arguments=[
            lineapy_tracer.literal(
                5,
                {"lineno": 2, "col_offset": 10, "end_lineno": 2, "end_col_offset": 11},
            ),
            lineapy_tracer.literal(
                2,
                {"lineno": 2, "col_offset": 13, "end_lineno": 2, "end_col_offset": 14},
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 15,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.call(
        function_name="root",
        syntax_dictionary={
            "lineno": 3,
            "col_offset": 4,
            "end_lineno": 3,
            "end_col_offset": 11,
        },
        arguments=[lineapy_tracer.lookup_node("a")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 11,
    },
)
lineapy_tracer.exit()
