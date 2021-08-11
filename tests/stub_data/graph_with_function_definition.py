from lineapy.data.graph import Graph
from tests.util import get_new_id
from tests.stub_data.simple_graph import session
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    CallNode,
    Library,
    ArgumentNode,
    LiteralAssignNode,
    FunctionDefinitionNode,
    StateChangeNode,
)


"""
This also doubles to test scope of the variable, as well as functions with mutation

```
import math
a = 0
def my_function():
    a = math.factorial(5)
my_function()
```

"""

line_1_id = get_new_id()

line_1_import = ImportNode(
    id=line_1_id,
    session_id=session.uuid,
    code="import math",
    library=Library(name="math"),
)

a_id = get_new_id()

line_2 = LiteralAssignNode(
    id=a_id, session_id=session.uuid, code="a = 0", assigned_variable_name="a", value=0
)

fun_id = get_new_id()
fun_def_note = FunctionDefinitionNode(
    id=fun_id,
    session_id=session.uuid,
    function_name="my_function",
    code="def my_function(a, b):\na = math.factorial(a) * b",
)

func_call_id = get_new_id()
my_function_call = CallNode(
    id=func_call_id,
    session_id=session.uuid,
    code="my_function()",
    function_name="my_function",
    locally_defined_function_id=fun_id,
)

a_state_change = StateChangeNode(
    id=get_new_id(),
    session_id=session.uuid,
    variable_name="a",
    associated_node_id=func_call_id,
)


graph_with_function_definition = Graph(
    [line_1_import, line_2, fun_def_note, my_function_call]
)
