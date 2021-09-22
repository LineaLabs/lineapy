from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[temp file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.assign(variable_name='b', value_node=lineapy_tracer.call(
    function_name='lt', syntax_dictionary={'lineno': 2, 'col_offset': 4,
    'end_lineno': 2, 'end_col_offset': 13}, arguments=[lineapy_tracer.call(
    function_name='lt', syntax_dictionary={'lineno': 2, 'col_offset': 4,
    'end_lineno': 2, 'end_col_offset': 13}, arguments=[1, 2],
    keyword_arguments=[]), 3], keyword_arguments=[]), syntax_dictionary={
    'lineno': 2, 'col_offset': 0, 'end_lineno': 2, 'end_col_offset': 13})
assert Variable('b')
lineapy_tracer.exit()
