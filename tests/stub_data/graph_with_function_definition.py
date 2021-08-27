from lineapy.data.graph import DirectedEdge
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    CallNode,
    Library,
    LiteralAssignNode,
    FunctionDefinitionNode,
    StateChangeNode,
)
from tests.util import get_new_id, get_new_session

"""
This also doubles to test scope of the variable, as well as functions with mutation

```
import math
a = 0
def my_function():
    global a
    a = math.factorial(5)
my_function()
```

"""

math_lib = Library(id=get_new_id(), name="math", version="1", path="home")

session = get_new_session(libraries=[math_lib])

line_1_id = get_new_id()

line_1_import = ImportNode(
    id=line_1_id,
    session_id=session.id,
    code="import math",
    library=math_lib,
)

a_id = get_new_id()

line_2 = LiteralAssignNode(
    id=a_id, session_id=session.id, code="a = 0", assigned_variable_name="a", value=0
)

fun_id = get_new_id()

a_state_change_id = get_new_id()
a_state_change = StateChangeNode(
    id=a_state_change_id,
    session_id=session.id,
    variable_name="a",
    associated_node_id=fun_id,
    initial_value_node_id=a_id,
)

fun_def_node = FunctionDefinitionNode(
    id=fun_id,
    session_id=session.id,
    function_name="my_function",
    code="def my_function():\n\tglobal a\n\ta = math.factorial(5)",
    state_change_nodes=[a_state_change_id],
    import_nodes=[line_1_id],
)

func_call_id = get_new_id()
my_function_call = CallNode(
    id=func_call_id,
    session_id=session.id,
    code="my_function()",
    function_name="my_function",
    locally_defined_function_id=fun_id,
    arguments=[],
)

e_a_to_fun = DirectedEdge(source_node_id=a_id, sink_node_id=fun_id)
e_import_to_fun = DirectedEdge(source_node_id=line_1_id, sink_node_id=fun_id)
e_fun_to_call = DirectedEdge(source_node_id=fun_id, sink_node_id=func_call_id)

graph_with_function_definition = Graph(
    [my_function_call, fun_def_node, line_1_import, line_2, a_state_change],
)
