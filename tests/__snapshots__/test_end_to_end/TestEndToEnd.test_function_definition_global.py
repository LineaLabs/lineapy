from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="math",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 11,
    },
    alias=None,
)
lineapy_tracer.trace_import(
    name="lineapy",
    syntax_dictionary={
        "lineno": 2,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 14,
    },
    alias=None,
)
lineapy_tracer.literal(
    assigned_variable_name="a",
    value=0,
    syntax_dictionary={
        "lineno": 3,
        "col_offset": 0,
        "end_lineno": 3,
        "end_col_offset": 5,
    },
)
lineapy_tracer.define_function(
    function_name="my_function",
    syntax_dictionary={
        "lineno": 4,
        "col_offset": 0,
        "end_lineno": 6,
        "end_col_offset": 25,
    },
)
lineapy_tracer.assign(
    variable_name="res",
    value_node=lineapy_tracer.call(
        function_name="my_function",
        syntax_dictionary={
            "lineno": 7,
            "col_offset": 6,
            "end_lineno": 7,
            "end_col_offset": 19,
        },
        arguments=[],
        keyword_arguments=[],
    ),
    syntax_dictionary={
        "lineno": 7,
        "col_offset": 0,
        "end_lineno": 7,
        "end_col_offset": 19,
    },
)
lineapy_tracer.publish(variable_name="res", description="res")
lineapy_tracer.exit()
