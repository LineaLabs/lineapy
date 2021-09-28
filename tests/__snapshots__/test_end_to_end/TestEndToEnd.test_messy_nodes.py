from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="lineapy",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 14,
    },
    alias=None,
)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.literal(
        1, {"lineno": 2, "col_offset": 4, "end_lineno": 2, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 5,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.call(
        function_name="add",
        syntax_dictionary={
            "lineno": 3,
            "col_offset": 4,
            "end_lineno": 3,
            "end_col_offset": 9,
        },
        arguments=[
            lineapy_tracer.lookup_node("a"),
            lineapy_tracer.literal(
                2, {"lineno": 3, "col_offset": 8, "end_lineno": 3, "end_col_offset": 9}
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 9,
    },
)
lineapy_tracer.assign(
    variable_name="c",
    value_node=lineapy_tracer.literal(
        2, {"lineno": 4, "col_offset": 4, "end_lineno": 4, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 5,
    },
)
lineapy_tracer.assign(
    variable_name="d",
    value_node=lineapy_tracer.literal(
        4, {"lineno": 5, "col_offset": 4, "end_lineno": 5, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 5,
        "col_offset": 0,
        "end_lineno": 5,
        "end_col_offset": 5,
    },
)
lineapy_tracer.assign(
    variable_name="e",
    value_node=lineapy_tracer.call(
        function_name="add",
        syntax_dictionary={
            "lineno": 6,
            "col_offset": 4,
            "end_lineno": 6,
            "end_col_offset": 9,
        },
        arguments=[lineapy_tracer.lookup_node("d"), lineapy_tracer.lookup_node("a")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 6,
        "col_offset": 0,
        "end_lineno": 6,
        "end_col_offset": 9,
    },
)
lineapy_tracer.assign(
    variable_name="f",
    value_node=lineapy_tracer.call(
        function_name="mul",
        syntax_dictionary={
            "lineno": 7,
            "col_offset": 4,
            "end_lineno": 7,
            "end_col_offset": 13,
        },
        arguments=[
            lineapy_tracer.call(
                function_name="mul",
                syntax_dictionary={
                    "lineno": 7,
                    "col_offset": 4,
                    "end_lineno": 7,
                    "end_col_offset": 9,
                },
                arguments=[
                    lineapy_tracer.lookup_node("a"),
                    lineapy_tracer.lookup_node("b"),
                ],
                keyword_arguments=[],
            ),
            lineapy_tracer.lookup_node("c"),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 7,
        "col_offset": 0,
        "end_lineno": 7,
        "end_col_offset": 13,
    },
)
lineapy_tracer.literal(
    10, {"lineno": 8, "col_offset": 0, "end_lineno": 8, "end_col_offset": 2}
)
lineapy_tracer.lookup_node("e")
lineapy_tracer.assign(
    variable_name="g",
    value_node=lineapy_tracer.lookup_node("e"),
    syntax_dictionary={
        "lineno": 10,
        "col_offset": 0,
        "end_lineno": 10,
        "end_col_offset": 5,
    },
)
lineapy_tracer.publish(variable_name="f", description="f")
lineapy_tracer.exit()
