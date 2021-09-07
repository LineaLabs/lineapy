from lineapy.data.graph import Graph
from lineapy.data.types import (
    LiteralAssignNode,
    CallNode,
    LoopNode,
    StateChangeNode,
    ArgumentNode,
    ImportNode,
    Library,
)
from tests.util import get_new_id, get_new_session

"""
Original code:

```python
a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
```

Graph method notes:
- Re-execution
  - Given that the nodes are NOT unrolled, the re-execution will simply do `exec` on the code provided at the loop enter.
  - The loops will have side-effects, these variables deemed to be affected by the side effect will have a new ID from "StateChangeNode". The re-exec need to look up the value of the variable_name in StateChangeNode and give it a value at run time, for later nodes to reference.

"""

code = """a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
"""

operator_lib = Library(id=get_new_id(), name="operator", version="1", path="")

session = get_new_session(code, libraries=[operator_lib])

a_id = get_new_id()

line_1 = CallNode(
    id=a_id,
    session_id=session.id,
    function_name="list",
    assigned_variable_name="a",
    arguments=[],
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=6,
)

b_id = get_new_id()

line_2 = LiteralAssignNode(
    id=b_id,
    session_id=session.id,
    assigned_variable_name="b",
    value=0,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=5,
)

le_id = get_new_id()

a_state_change_id = get_new_id()
a_argument_id = get_new_id()

a_state_change = StateChangeNode(
    id=a_state_change_id,
    session_id=session.id,
    variable_name="a",
    associated_node_id=le_id,
    initial_value_node_id=a_id,
)
a_argument_node = ArgumentNode(
    id=a_argument_id,
    session_id=session.id,
    positional_order=0,
    value_node_id=a_state_change_id,
    lineno=6,
    col_offset=8,
    end_lineno=6,
    end_col_offset=9,
)

b_state_change_id = get_new_id()
b_argument_id = get_new_id()

b_state_change = StateChangeNode(
    id=b_state_change_id,
    session_id=session.id,
    variable_name="b",
    associated_node_id=le_id,
    initial_value_node_id=b_id,
)
b_argument_node = ArgumentNode(
    id=b_argument_id,
    session_id=session.id,
    positional_order=1,
    value_node_id=b_state_change_id,
    lineno=7,
    col_offset=8,
    end_lineno=7,
    end_col_offset=9,
)

le = LoopNode(
    id=le_id,
    session_id=session.id,
    state_change_nodes=[a_state_change_id, b_state_change_id],
    lineno=3,
    col_offset=0,
    end_lineno=5,
    end_col_offset=5,
)

x_id = get_new_id()

line_6 = CallNode(
    id=x_id,
    session_id=session.id,
    function_name="sum",
    assigned_variable_name="x",
    arguments=[a_argument_id],
)

operator_module_id = get_new_id()

operator_module = ImportNode(
    id=operator_module_id,
    session_id=session.id,
    library=operator_lib,
)

x_argument_id = get_new_id()
x_argument_node = ArgumentNode(
    id=x_argument_id,
    session_id=session.id,
    positional_order=0,
    value_node_id=x_id,
    lineno=7,
    col_offset=4,
    end_lineno=7,
    end_col_offset=5,
)

y_id = get_new_id()
line_7 = CallNode(
    id=y_id,
    session_id=session.id,
    function_name="add",
    function_module=operator_module_id,  # built in
    assigned_variable_name="y",
    arguments=[x_argument_id, b_argument_id],
    lineno=7,
    col_offset=0,
    end_lineno=7,
    end_col_offset=9,
)

graph_with_loops = Graph(
    [
        a_argument_node,
        x_argument_node,
        b_argument_node,
        line_1,
        line_2,
        le,
        a_state_change,
        b_state_change,
        line_6,
        operator_module,
        line_7,
    ]
)
