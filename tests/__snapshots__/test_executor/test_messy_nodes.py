from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[source file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.literal(assigned_variable_name='a', value=1,
    syntax_dictionary={'lineno': 2, 'col_offset': 0, 'end_lineno': 2,
    'end_col_offset': 5})
lineapy_tracer.assign(variable_name='b', value_node=lineapy_tracer.call(
    function_name='add', syntax_dictionary={'lineno': 3, 'col_offset': 4,
    'end_lineno': 3, 'end_col_offset': 9}, arguments=[Variable('a'), 2],
    keyword_arguments=[]), syntax_dictionary={'lineno': 3, 'col_offset': 0,
    'end_lineno': 3, 'end_col_offset': 9})
lineapy_tracer.literal(assigned_variable_name='c', value=2,
    syntax_dictionary={'lineno': 4, 'col_offset': 0, 'end_lineno': 4,
    'end_col_offset': 5})
lineapy_tracer.literal(assigned_variable_name='d', value=4,
    syntax_dictionary={'lineno': 5, 'col_offset': 0, 'end_lineno': 5,
    'end_col_offset': 5})
lineapy_tracer.assign(variable_name='e', value_node=lineapy_tracer.call(
    function_name='add', syntax_dictionary={'lineno': 6, 'col_offset': 4,
    'end_lineno': 6, 'end_col_offset': 9}, arguments=[Variable('d'),
    Variable('a')], keyword_arguments=[]), syntax_dictionary={'lineno': 6,
    'col_offset': 0, 'end_lineno': 6, 'end_col_offset': 9})
lineapy_tracer.assign(variable_name='f', value_node=lineapy_tracer.call(
    function_name='mul', syntax_dictionary={'lineno': 7, 'col_offset': 4,
    'end_lineno': 7, 'end_col_offset': 13}, arguments=[lineapy_tracer.call(
    function_name='mul', syntax_dictionary={'lineno': 7, 'col_offset': 4,
    'end_lineno': 7, 'end_col_offset': 9}, arguments=[Variable('a'),
    Variable('b')], keyword_arguments=[]), Variable('c')],
    keyword_arguments=[]), syntax_dictionary={'lineno': 7, 'col_offset': 0,
    'end_lineno': 7, 'end_col_offset': 13})
lineapy_tracer.headless_literal(10, {'lineno': 8, 'col_offset': 0,
    'end_lineno': 8, 'end_col_offset': 2})
lineapy_tracer.headless_variable('e', {'lineno': 9, 'col_offset': 0,
    'end_lineno': 9, 'end_col_offset': 1})
lineapy_tracer.assign(variable_name='g', value_node=Variable('e'),
    syntax_dictionary={'lineno': 10, 'col_offset': 0, 'end_lineno': 10,
    'end_col_offset': 5})
lineapy_tracer.exit()
