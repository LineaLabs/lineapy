from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.call(
        function_name="min",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 4,
            "end_lineno": 1,
            "end_col_offset": 20,
        },
        arguments=[
            lineapy_tracer.call(
                function_name="abs",
                syntax_dictionary={
                    "lineno": 1,
                    "col_offset": 8,
                    "end_lineno": 1,
                    "end_col_offset": 15,
                },
                arguments=[
                    lineapy_tracer.literal(
                        11,
                        {
                            "lineno": 1,
                            "col_offset": 12,
                            "end_lineno": 1,
                            "end_col_offset": 14,
                        },
                    )
                ],
                keyword_arguments=[],
            ),
            lineapy_tracer.literal(
                10,
                {"lineno": 1, "col_offset": 17, "end_lineno": 1, "end_col_offset": 19},
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 20,
    },
)
lineapy_tracer.exit()
