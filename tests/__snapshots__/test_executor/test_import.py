from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="math",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 43,
    },
    attributes={"power": "pow", "root": "sqrt"},
)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.call(
        function_name="power",
        syntax_dictionary={
            "lineno": 3,
            "col_offset": 4,
            "end_lineno": 3,
            "end_col_offset": 15,
        },
        arguments=[5, 2],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 15,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.call(
        function_name="root",
        syntax_dictionary={
            "lineno": 4,
            "col_offset": 4,
            "end_lineno": 4,
            "end_col_offset": 11,
        },
        arguments=[Variable("a")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 11,
    },
)
lineapy_tracer.exit()
