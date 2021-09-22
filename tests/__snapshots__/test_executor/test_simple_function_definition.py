from lineapy import SessionType, Tracer, Variable, ExecutionMode
lineapy_tracer = Tracer(SessionType.SCRIPT,
    '[source file path]'
    , ExecutionMode.MEMORY)
lineapy_tracer.define_function(function_name='foo', syntax_dictionary={
    'lineno': 2, 'col_offset': 0, 'end_lineno': 3, 'end_col_offset': 16})
lineapy_tracer.assign(variable_name='c', value_node=lineapy_tracer.call(
    function_name='foo', syntax_dictionary={'lineno': 4, 'col_offset': 4,
    'end_lineno': 4, 'end_col_offset': 17}, arguments=[], keyword_arguments
    =[('b', 1), ('a', 2)]), syntax_dictionary={'lineno': 4, 'col_offset': 0,
    'end_lineno': 4, 'end_col_offset': 17})
lineapy_tracer.exit()
