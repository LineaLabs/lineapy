from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="setitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 17,
    },
    arguments=[
        Variable("ls"),
        lineapy_tracer.call(
            function_name="__build_list__",
            syntax_dictionary={
                "lineno": 1,
                "col_offset": 3,
                "end_lineno": 1,
                "end_col_offset": 8,
            },
            arguments=[1, 2],
            keyword_arguments=[],
        ),
        lineapy_tracer.call(
            function_name="__build_list__",
            syntax_dictionary={
                "lineno": 1,
                "col_offset": 12,
                "end_lineno": 1,
                "end_col_offset": 17,
            },
            arguments=[1, 2],
            keyword_arguments=[],
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
