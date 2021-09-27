from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="types",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 12,
    },
    alias=None,
)
lineapy_tracer.assign(
    variable_name="x",
    value_node=lineapy_tracer.call(
        function_name="SimpleNamespace",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 18,
            "end_lineno": 1,
            "end_col_offset": 41,
        },
        arguments=[],
        keyword_arguments=[],
        function_module="types",
    ),
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 14,
        "end_lineno": 1,
        "end_col_offset": 41,
    },
)
lineapy_tracer.call(
    function_name="setattr",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 43,
        "end_lineno": 1,
        "end_col_offset": 51,
    },
    arguments=[Variable("x"), "hi", 1],
    keyword_arguments=[],
)
lineapy_tracer.call(
    function_name="delattr",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 53,
        "end_lineno": 1,
        "end_col_offset": 61,
    },
    arguments=[Variable("x"), "hi"],
    keyword_arguments=[],
)
lineapy_tracer.exit()
