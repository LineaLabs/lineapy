from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[temp file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.assign(variable_name='ls', value_node=lineapy_tracer.call(
    function_name='__build_list__', syntax_dictionary={'lineno': 2,
    'col_offset': 5, 'end_lineno': 2, 'end_col_offset': 10}, arguments=[1, 
    2], keyword_arguments=[]), syntax_dictionary={'lineno': 2, 'col_offset':
    0, 'end_lineno': 2, 'end_col_offset': 10})
assert lineapy_tracer.call(function_name='eq', syntax_dictionary={'lineno':
    3, 'col_offset': 7, 'end_lineno': 3, 'end_col_offset': 17}, arguments=[
    lineapy_tracer.call(function_name='getitem', syntax_dictionary={
    'lineno': 3, 'col_offset': 7, 'end_lineno': 3, 'end_col_offset': 12},
    arguments=[Variable('ls'), 0], keyword_arguments=[]), 1],
    keyword_arguments=[])
lineapy_tracer.exit()
