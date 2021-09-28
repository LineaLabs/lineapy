from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="is_not",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 10,
    },
    arguments=[lineapy_tracer.lookup_node("a"), lineapy_tracer.lookup_node("b")],
    keyword_arguments=[],
)
lineapy_tracer.exit()
