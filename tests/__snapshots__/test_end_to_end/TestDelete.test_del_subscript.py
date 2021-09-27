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
            "end_col_offset": 7,
        },
        arguments=[1],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 7,
    },
)
lineapy_tracer.call(
    function_name="delitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 9,
        "end_lineno": 1,
        "end_col_offset": 17,
    },
    arguments=[Variable("a"), 0],
    keyword_arguments=[],
)
lineapy_tracer.exit()
