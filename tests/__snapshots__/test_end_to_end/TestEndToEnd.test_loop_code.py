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
    value_node=lineapy_tracer.call(
        function_name="__build_list__",
        syntax_dictionary={
            "lineno": 2,
            "col_offset": 4,
            "end_lineno": 2,
            "end_col_offset": 6,
        },
        arguments=[],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 6,
    },
)
lineapy_tracer.assign(
    variable_name="b",
    value_node=lineapy_tracer.literal(
        0, {"lineno": 3, "col_offset": 4, "end_lineno": 3, "end_col_offset": 5}
    ),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 5,
    },
)
for lineapy_tracer.lookup_node("x") in lineapy_tracer.call(
    function_name="range",
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 9,
        "end_lineno": 4,
        "end_col_offset": 17,
    },
    arguments=[
        lineapy_tracer.literal(
            9, {"lineno": 4, "col_offset": 15, "end_lineno": 4, "end_col_offset": 16}
        )
    ],
    keyword_arguments=[],
):
    lineapy_tracer.call(
        function_name="append",
        syntax_dictionary={
            "lineno": 5,
            "col_offset": 4,
            "end_lineno": 5,
            "end_col_offset": 15,
        },
        arguments=[lineapy_tracer.lookup_node("x")],
        keyword_arguments=[],
        function_module="a",
    )
    lineapy_tracer.lookup_node("b") += lineapy_tracer.lookup_node("x")
lineapy_tracer.assign(
    variable_name="x",
    value_node=lineapy_tracer.call(
        function_name="sum",
        syntax_dictionary={
            "lineno": 7,
            "col_offset": 4,
            "end_lineno": 7,
            "end_col_offset": 10,
        },
        arguments=[lineapy_tracer.lookup_node("a")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 7,
        "col_offset": 0,
        "end_lineno": 7,
        "end_col_offset": 10,
    },
)
lineapy_tracer.assign(
    variable_name="y",
    value_node=lineapy_tracer.call(
        function_name="add",
        syntax_dictionary={
            "lineno": 8,
            "col_offset": 4,
            "end_lineno": 8,
            "end_col_offset": 9,
        },
        arguments=[lineapy_tracer.lookup_node("x"), lineapy_tracer.lookup_node("b")],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 8,
        "col_offset": 0,
        "end_lineno": 8,
        "end_col_offset": 9,
    },
)
lineapy_tracer.publish(variable_name="y", description="y")
lineapy_tracer.exit()
