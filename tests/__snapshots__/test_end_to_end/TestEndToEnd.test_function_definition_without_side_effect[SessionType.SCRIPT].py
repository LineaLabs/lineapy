from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.define_function(
    function_name="foo",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 16,
    },
)
lineapy_tracer.assign(
    variable_name="c",
    value_node=lineapy_tracer.call(
        function_name="foo",
        syntax_dictionary={
            "lineno": 3,
            "col_offset": 4,
            "end_lineno": 3,
            "end_col_offset": 17,
        },
        arguments=[],
        keyword_arguments=[
            (
                "b",
                lineapy_tracer.literal(
                    1,
                    {
                        "lineno": 3,
                        "col_offset": 10,
                        "end_lineno": 3,
                        "end_col_offset": 11,
                    },
                ),
            ),
            (
                "a",
                lineapy_tracer.literal(
                    2,
                    {
                        "lineno": 3,
                        "col_offset": 15,
                        "end_lineno": 3,
                        "end_col_offset": 16,
                    },
                ),
            ),
        ],
    ),
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 17,
    },
)
lineapy_tracer.exit()
