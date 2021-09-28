from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="pandas",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 19,
    },
    alias="pd",
)
lineapy_tracer.trace_import(
    name="matplotlib.pyplot",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 31,
    },
    alias="plt",
)
lineapy_tracer.assign(
    variable_name="df",
    value_node=lineapy_tracer.call(
        function_name="read_csv",
        syntax_dictionary={
            "lineno": 4,
            "col_offset": 5,
            "end_lineno": 4,
            "end_col_offset": 41,
        },
        arguments=[
            lineapy_tracer.literal(
                "tests/simple_data.csv",
                {"lineno": 4, "col_offset": 17, "end_lineno": 4, "end_col_offset": 40},
            )
        ],
        keyword_arguments=[],
        function_module="pd",
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 41,
    },
)
lineapy_tracer.call(
    function_name="imsave",
    syntax_dictionary={
        "lineno": 5,
        "col_offset": 0,
        "end_lineno": 5,
        "end_col_offset": 33,
    },
    arguments=[
        lineapy_tracer.literal(
            "simple_data.png",
            {"lineno": 5, "col_offset": 11, "end_lineno": 5, "end_col_offset": 28},
        ),
        lineapy_tracer.lookup_node("df"),
    ],
    keyword_arguments=[],
    function_module="plt",
)
lineapy_tracer.exit()
