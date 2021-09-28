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
lineapy_tracer.trace_import(
    name="PIL.Image",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 26,
    },
    attributes={"open": "open"},
)
lineapy_tracer.assign(
    variable_name="img",
    value_node=lineapy_tracer.call(
        function_name="open",
        syntax_dictionary={
            "lineno": 4,
            "col_offset": 6,
            "end_lineno": 4,
            "end_col_offset": 29,
        },
        arguments=[
            lineapy_tracer.literal(
                "simple_data.png",
                {"lineno": 4, "col_offset": 11, "end_lineno": 4, "end_col_offset": 28},
            )
        ],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 29,
    },
)
lineapy_tracer.assign(
    variable_name="img",
    value_node=lineapy_tracer.call(
        function_name="resize",
        syntax_dictionary={
            "lineno": 5,
            "col_offset": 6,
            "end_lineno": 5,
            "end_col_offset": 28,
        },
        arguments=[
            lineapy_tracer.call(
                function_name="__build_list__",
                syntax_dictionary={
                    "lineno": 5,
                    "col_offset": 17,
                    "end_lineno": 5,
                    "end_col_offset": 27,
                },
                arguments=[
                    lineapy_tracer.literal(
                        200,
                        {
                            "lineno": 5,
                            "col_offset": 18,
                            "end_lineno": 5,
                            "end_col_offset": 21,
                        },
                    ),
                    lineapy_tracer.literal(
                        200,
                        {
                            "lineno": 5,
                            "col_offset": 23,
                            "end_lineno": 5,
                            "end_col_offset": 26,
                        },
                    ),
                ],
                keyword_arguments=[],
            )
        ],
        keyword_arguments=[],
        function_module="img",
    ),
    syntax_dictionary={
        "lineno": 5,
        "col_offset": 0,
        "end_lineno": 5,
        "end_col_offset": 28,
    },
)
lineapy_tracer.publish(variable_name="img", description="Graph With Image")
lineapy_tracer.exit()
