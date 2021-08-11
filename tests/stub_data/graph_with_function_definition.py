from lineapy.data.graph import Graph
from tests.util import get_new_id
from tests.stub_data.simple_graph import session
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    CallNode,
    Library,
    ArgumentNode,
    FunctionDefinitionNode
)


"""
This also doubles to test scope of the variable, as well as functions with mutation

```
import math
a = 0
def my_function(a, b):
    a = math.factorial(a) * b
b = my_function()
```

"""

line_1_id = get_new_id()

line_1_import = ImportNode(
    id=line_1_id,
    session_id = session.uuid, 
    code="import math", 
    library=Library(
        name="math"
    )
)

a_id = get_new_id()

line_2 = LiteralAssignNode(
    id=a_id, session_id=session.uuid, code="a = 0", assigned_variable_name="a", value=0
)

fun_id = get_new_id()
fun_def_note = FunctionDefinitionNode(
    id = fun_id,
    session_id = session.uuid, 
    function_name="my_function",
    code = "def my_function(a, b):\na = math.factorial(a) * b"
)

my_function_call = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="my_function()",
    function_name="my_function",
    assigned_variable_name
)


graph_with_function_definition = Graph([])