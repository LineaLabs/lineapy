from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="getitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 7,
    },
    arguments=[
        Variable("ls"),
        lineapy_tracer.call(
            function_name="slice",
            syntax_dictionary={
                "lineno": 1,
                "col_offset": 3,
                "end_lineno": 1,
                "end_col_offset": 6,
            },
            arguments=[1, 2],
            keyword_arguments=[],
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
