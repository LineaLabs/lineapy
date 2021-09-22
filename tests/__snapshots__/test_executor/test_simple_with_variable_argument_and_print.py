from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[source file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.assign(variable_name='a', value_node=lineapy_tracer.call(
    function_name='abs', syntax_dictionary={'lineno': 2, 'col_offset': 4,
    'end_lineno': 2, 'end_col_offset': 12}, arguments=[-11],
    keyword_arguments=[]), syntax_dictionary={'lineno': 2, 'col_offset': 0,
    'end_lineno': 2, 'end_col_offset': 12})
lineapy_tracer.assign(variable_name='b', value_node=lineapy_tracer.call(
    function_name='min', syntax_dictionary={'lineno': 3, 'col_offset': 4,
    'end_lineno': 3, 'end_col_offset': 14}, arguments=[Variable('a'), 10],
    keyword_arguments=[]), syntax_dictionary={'lineno': 3, 'col_offset': 0,
    'end_lineno': 3, 'end_col_offset': 14})
lineapy_tracer.call(function_name='print', syntax_dictionary={'lineno': 4,
    'col_offset': 0, 'end_lineno': 4, 'end_col_offset': 8}, arguments=[
    Variable('b')], keyword_arguments=[])
lineapy_tracer.exit()
