from lineapy import SessionType, Tracer, Variable, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.call(
    function_name="setitem",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 9,
    },
    arguments=[Variable("ls"), Variable("a"), Variable("b")],
    keyword_arguments=[],
)
lineapy_tracer.exit()
