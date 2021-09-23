from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.STATIC, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="getitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 11,
    },
    arguments=[
        lineapy_tracer.call(
            function_name="__build_list__",
            syntax_dictionary={
                "lineno": 1,
                "col_offset": 0,
                "end_lineno": 1,
                "end_col_offset": 3,
            },
            arguments=[0],
            keyword_arguments=[],
        ),
        lineapy_tracer.call(
            function_name="abs",
            syntax_dictionary={
                "lineno": 1,
                "col_offset": 4,
                "end_lineno": 1,
                "end_col_offset": 10,
            },
            arguments=[0],
            keyword_arguments=[],
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
