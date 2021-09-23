from lineapy import SessionType, Tracer, Variable, ExecutionMode

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
lineapy_tracer.trace_import(
    name="PIL.Image",
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 26,
    },
    attributes={"open": "open"},
)
lineapy_tracer.assign(
    variable_name="df",
    value_node=lineapy_tracer.call(
        function_name="read_csv",
        syntax_dictionary={
            "lineno": 4,
            "col_offset": 5,
            "end_lineno": 4,
            "end_col_offset": 51,
        },
        arguments=["tests/stub_data/simple_data.csv"],
        keyword_arguments=[],
        function_module="pd",
    ),
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 4,
        "end_col_offset": 51,
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
    arguments=["simple_data.png", Variable("df")],
    keyword_arguments=[],
    function_module="plt",
)
lineapy_tracer.assign(
    variable_name="img",
    value_node=lineapy_tracer.call(
        function_name="open",
        syntax_dictionary={
            "lineno": 6,
            "col_offset": 6,
            "end_lineno": 6,
            "end_col_offset": 29,
        },
        arguments=["simple_data.png"],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 6,
        "col_offset": 0,
        "end_lineno": 6,
        "end_col_offset": 29,
    },
)
lineapy_tracer.assign(
    variable_name="img",
    value_node=lineapy_tracer.call(
        function_name="resize",
        syntax_dictionary={
            "lineno": 7,
            "col_offset": 6,
            "end_lineno": 7,
            "end_col_offset": 28,
        },
        arguments=[
            lineapy_tracer.call(
                function_name="__build_list__",
                syntax_dictionary={
                    "lineno": 7,
                    "col_offset": 17,
                    "end_lineno": 7,
                    "end_col_offset": 27,
                },
                arguments=[200, 200],
                keyword_arguments=[],
            )
        ],
        keyword_arguments=[],
        function_module="img",
    ),
    syntax_dictionary={
        "lineno": 7,
        "col_offset": 0,
        "end_lineno": 7,
        "end_col_offset": 28,
    },
)
lineapy_tracer.exit()
