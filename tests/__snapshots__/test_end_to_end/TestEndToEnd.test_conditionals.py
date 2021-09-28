from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="bs",
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
if lineapy_tracer.call(
    function_name="gt",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 3,
        "end_lineno": 2,
        "end_col_offset": 14,
    },
    arguments=[
        lineapy_tracer.call(
            function_name="len",
            syntax_dictionary={
                "lineno": 2,
                "col_offset": 3,
                "end_lineno": 2,
                "end_col_offset": 10,
            },
            arguments=[lineapy_tracer.lookup_node("bs")],
            keyword_arguments=[],
        ),
        lineapy_tracer.literal(
            4, {"lineno": 2, "col_offset": 13, "end_lineno": 2, "end_col_offset": 14}
        ),
    ],
    keyword_arguments=[],
):
    lineapy_tracer.call(
        function_name="print",
        syntax_dictionary={
            "lineno": 3,
            "col_offset": 4,
            "end_lineno": 3,
            "end_col_offset": 17,
        },
        arguments=[
            lineapy_tracer.literal(
                "True",
                {"lineno": 3, "col_offset": 10, "end_lineno": 3, "end_col_offset": 16},
            )
        ],
        keyword_arguments=[],
    )
else:
    lineapy_tracer.call(
        function_name="append",
        syntax_dictionary={
            "lineno": 5,
            "col_offset": 4,
            "end_lineno": 5,
            "end_col_offset": 16,
        },
        arguments=[
            lineapy_tracer.literal(
                3,
                {"lineno": 5, "col_offset": 14, "end_lineno": 5, "end_col_offset": 15},
            )
        ],
        keyword_arguments=[],
        function_module="bs",
    )
    lineapy_tracer.call(
        function_name="print",
        syntax_dictionary={
            "lineno": 6,
            "col_offset": 4,
            "end_lineno": 6,
            "end_col_offset": 18,
        },
        arguments=[
            lineapy_tracer.literal(
                "False",
                {"lineno": 6, "col_offset": 10, "end_lineno": 6, "end_col_offset": 17},
            )
        ],
        keyword_arguments=[],
    )
lineapy_tracer.exit()
