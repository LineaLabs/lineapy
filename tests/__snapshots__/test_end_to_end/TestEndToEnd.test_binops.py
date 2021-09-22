from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.call(
        function_name="add",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 4,
            "end_lineno": 1,
            "end_col_offset": 9,
        },
        arguments=[1, 2],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 9,
    },
)
assert lineapy_tracer.call(
    function_name="eq",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 7,
        "end_lineno": 2,
        "end_col_offset": 13,
    },
    arguments=[Variable("b"), 3],
    keyword_arguments=[],
)
lineapy_tracer.exit()
