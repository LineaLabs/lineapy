from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[source file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.assign(variable_name='bs', value_node=lineapy_tracer.call(
    function_name='__build_list__', syntax_dictionary={'lineno': 2,
    'col_offset': 5, 'end_lineno': 2, 'end_col_offset': 10}, arguments=[1, 
    2], keyword_arguments=[]), syntax_dictionary={'lineno': 2, 'col_offset':
    0, 'end_lineno': 2, 'end_col_offset': 10})
if lineapy_tracer.call(function_name='gt', syntax_dictionary={'lineno': 3,
    'col_offset': 3, 'end_lineno': 3, 'end_col_offset': 14}, arguments=[
    lineapy_tracer.call(function_name='len', syntax_dictionary={'lineno': 3,
    'col_offset': 3, 'end_lineno': 3, 'end_col_offset': 10}, arguments=[
    Variable('bs')], keyword_arguments=[]), 4], keyword_arguments=[]):
    lineapy_tracer.call(function_name='print', syntax_dictionary={'lineno':
        4, 'col_offset': 4, 'end_lineno': 4, 'end_col_offset': 17},
        arguments=['True'], keyword_arguments=[])
else:
    lineapy_tracer.call(function_name='append', syntax_dictionary={'lineno':
        6, 'col_offset': 4, 'end_lineno': 6, 'end_col_offset': 16},
        arguments=[3], keyword_arguments=[], function_module='bs')
    lineapy_tracer.call(function_name='print', syntax_dictionary={'lineno':
        7, 'col_offset': 4, 'end_lineno': 7, 'end_col_offset': 18},
        arguments=['False'], keyword_arguments=[])
lineapy_tracer.exit()
