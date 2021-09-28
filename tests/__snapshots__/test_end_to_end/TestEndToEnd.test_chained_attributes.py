from lineapy import SessionType, Tracer, ExecutionMode

lineapy_tracer = Tracer(SessionType.SCRIPT, "[source file path]", ExecutionMode.MEMORY)
lineapy_tracer.trace_import(
    name="altair",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 1,
        "end_col_offset": 13,
    },
    alias=None,
)
lineapy_tracer.call(
    function_name="enable",
    syntax_dictionary={
        "lineno": 1,
        "col_offset": 15,
        "end_lineno": 1,
        "end_col_offset": 54,
    },
    arguments=[
        lineapy_tracer.literal(
            "json",
            {"lineno": 1, "col_offset": 47, "end_lineno": 1, "end_col_offset": 53},
        )
    ],
    keyword_arguments=[],
    function_module=lineapy_tracer.call(
        function_name="getattr",
        syntax_dictionary={
            "lineno": 1,
            "col_offset": 15,
            "end_lineno": 1,
            "end_col_offset": 39,
        },
        arguments=[
            lineapy_tracer.lookup_node("altair"),
            lineapy_tracer.literal(
                "data_transformers",
                {
                    "lineno": None,
                    "col_offset": None,
                    "end_lineno": None,
                    "end_col_offset": None,
                },
            ),
        ],
        keyword_arguments=[],
    ),
)
lineapy_tracer.exit()
