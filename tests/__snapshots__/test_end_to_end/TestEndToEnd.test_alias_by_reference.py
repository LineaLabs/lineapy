from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.call(
        function_name="__build_list__",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 4,
            "end_lineno": 1,
            "end_col_offset": 11,
        },
        arguments=[
            lineapy_tracer.literal(
                1, {"lineno": 1, "col_offset": 5, "end_lineno": 1, "end_col_offset": 6}
            ),
            lineapy_tracer.literal(
                2, {"lineno": 1, "col_offset": 7, "end_lineno": 1, "end_col_offset": 8}
            ),
            lineapy_tracer.literal(
                3, {"lineno": 1, "col_offset": 9, "end_lineno": 1, "end_col_offset": 10}
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 11,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.lookup_node("a"),
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 5,
    },
)
lineapy_tracer.call(
    function_name="append",
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 11,
    },
    arguments=[
        lineapy_tracer.literal(
            4, {"lineno": 3, "col_offset": 9, "end_lineno": 3, "end_col_offset": 10}
        )
    ],
    keyword_arguments=[],
    function_module="a",
)
lineapy_tracer.assign(
    variable_name="s",
    value_node=lineapy_tracer.call(
        function_name="sum",
        syntax_dictionary={
            "lineno": 4,
            "col_offset": 4,
            "end_lineno": 4,
            "end_col_offset": 10,
        },
        arguments=[lineapy_tracer.lookup_node("b")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 10,
    },
)
lineapy_tracer.exit()
