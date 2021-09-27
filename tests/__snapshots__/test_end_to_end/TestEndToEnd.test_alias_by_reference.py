from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.call(
        function_name="__build_list__",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 4,
            "end_lineno": 1,
            "end_col_offset": 11,
        },
        arguments=[1, 2, 3],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 11,
    },
)
lineapy_tracer.variable_alias(
    assigned_variable_name="b",
    source_variable_name="a",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 5,
    },
)
lineapy_tracer.call(
    function_name="append",
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 11,
    },
    arguments=[4],
    keyword_arguments=[],
    function_module="a",
)
lineapy_tracer.assign(
    variable_name="s",
    value_node=lineapy_tracer.call(
        function_name="sum",
        syntax_dictionary={
            "lineno": 4,
            "col_offset": 4,
            "end_lineno": 4,
            "end_col_offset": 10,
        },
        arguments=[Variable("b")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 10,
    },
)
lineapy_tracer.exit()
