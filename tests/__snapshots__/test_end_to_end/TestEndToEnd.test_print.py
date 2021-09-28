from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.assign(
    variable_name="a",
    value_node=lineapy_tracer.call(
        function_name="abs",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 4,
            "end_lineno": 1,
            "end_col_offset": 11,
        },
        arguments=[
            lineapy_tracer.literal(
                11,
                {"lineno": 1, "col_offset": 8, "end_lineno": 1, "end_col_offset": 10},
            )
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
    value_node=lineapy_tracer.call(
        function_name="min",
        syntax_dictionary={
            "lineno": 2,
            "col_offset": 4,
            "end_lineno": 2,
            "end_col_offset": 14,
        },
        arguments=[
            lineapy_tracer.lookup_node("a"),
            lineapy_tracer.literal(
                10,
                {"lineno": 2, "col_offset": 11, "end_lineno": 2, "end_col_offset": 13},
            ),
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 14,
    },
)
lineapy_tracer.call(
    function_name="print",
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 8,
    },
    arguments=[lineapy_tracer.lookup_node("b")],
    keyword_arguments=[],
)
lineapy_tracer.exit()
