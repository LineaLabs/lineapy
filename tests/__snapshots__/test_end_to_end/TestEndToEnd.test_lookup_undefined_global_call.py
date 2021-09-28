from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.STATIC, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="system",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 24,
    },
    arguments=[
        lineapy_tracer.literal(
            "", {"lineno": 1, "col_offset": 21, "end_lineno": 1, "end_col_offset": 23}
        )
    ],
    keyword_arguments=[],
    function_module=lineapy_tracer.call(
        function_name="get_ipython",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 0,
            "end_lineno": 1,
            "end_col_offset": 13,
        },
        arguments=[],
        keyword_arguments=[],
    ),
)
lineapy_tracer.exit()
