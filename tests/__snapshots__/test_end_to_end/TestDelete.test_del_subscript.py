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
            "end_col_offset": 7,
        },
        arguments=[
            lineapy_tracer.literal(
                1, {"lineno": 1, "col_offset": 5, "end_lineno": 1, "end_col_offset": 6}
            )
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 7,
    },
)
lineapy_tracer.call(
    function_name="delitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 9,
        "end_lineno": 1,
        "end_col_offset": 17,
    },
    arguments=[
        lineapy_tracer.lookup_node("a"),
        lineapy_tracer.literal(
            0, {"lineno": 1, "col_offset": 15, "end_lineno": 1, "end_col_offset": 16}
        ),
    ],
    keyword_arguments=[],
)
lineapy_tracer.exit()
