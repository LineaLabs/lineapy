from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[source file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.assign(variable_name='a', value_node=lineapy_tracer.call(
    function_name='min', syntax_dictionary={'lineno': 1, 'col_offset': 4,
    'end_lineno': 1, 'end_col_offset': 21}, arguments=[lineapy_tracer.call(
    function_name='abs', syntax_dictionary={'lineno': 1, 'col_offset': 8,
    'end_lineno': 1, 'end_col_offset': 16}, arguments=[-11],
    keyword_arguments=[]), 10], keyword_arguments=[]), syntax_dictionary={
    'lineno': 1, 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 21})
lineapy_tracer.exit()
