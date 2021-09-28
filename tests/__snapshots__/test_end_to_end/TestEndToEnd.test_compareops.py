from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.call(
        function_name="lt",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 4,
            "end_lineno": 1,
            "end_col_offset": 13,
        },
        arguments=[
            lineapy_tracer.call(
                function_name="lt",
                syntax_dictionary={
                    "lineno": 1,
                    "col_offset": 4,
                    "end_lineno": 1,
                    "end_col_offset": 13,
                },
                arguments=[
                    lineapy_tracer.literal(
                        1,
                        {
                            "lineno": 1,
                            "col_offset": 4,
                            "end_lineno": 1,
                            "end_col_offset": 5,
                        },
                    ),
                    lineapy_tracer.literal(
                        2,
                        {
                            "lineno": 1,
                            "col_offset": 8,
                            "end_lineno": 1,
                            "end_col_offset": 9,
                        },
                    ),
                ],
                keyword_arguments=[],
            ),
            lineapy_tracer.literal(
                3,
                {"lineno": 1, "col_offset": 12, "end_lineno": 1, "end_col_offset": 13},
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 13,
    },
)
assert lineapy_tracer.lookup_node("b")
lineapy_tracer.exit()
