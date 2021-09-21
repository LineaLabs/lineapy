from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[temp file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.literal(assigned_variable_name='a', value=1,
    syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1,
    'end_col_offset': 5})
lineapy_tracer.exit()
