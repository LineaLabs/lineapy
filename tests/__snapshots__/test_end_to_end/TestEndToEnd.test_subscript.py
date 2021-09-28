from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="ls",
    value_node=lineapy_tracer.call(
        function_name="__build_list__",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 5,
            "end_lineno": 1,
            "end_col_offset": 10,
        },
        arguments=[
            lineapy_tracer.literal(
                1, {"lineno": 1, "col_offset": 6, "end_lineno": 1, "end_col_offset": 7}
            ),
            lineapy_tracer.literal(
                2, {"lineno": 1, "col_offset": 8, "end_lineno": 1, "end_col_offset": 9}
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 10,
    },
)
assert lineapy_tracer.call(
    function_name="eq",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 7,
        "end_lineno": 2,
        "end_col_offset": 17,
    },
    arguments=[
        lineapy_tracer.call(
            function_name="getitem",
            syntax_dictionary={
                "lineno": 2,
                "col_offset": 7,
                "end_lineno": 2,
                "end_col_offset": 12,
            },
            arguments=[
                lineapy_tracer.lookup_node("ls"),
                lineapy_tracer.literal(
                    0,
                    {
                        "lineno": 2,
                        "col_offset": 10,
                        "end_lineno": 2,
                        "end_col_offset": 11,
                    },
                ),
            ],
            keyword_arguments=[],
        ),
        lineapy_tracer.literal(
            1, {"lineno": 2, "col_offset": 16, "end_lineno": 2, "end_col_offset": 17}
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
