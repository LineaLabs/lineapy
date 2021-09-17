from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    ConditionNode,
    StateChangeNode,
    StateDependencyType,
)

from tests.util import get_new_id, get_new_session

"""
Original code:

```python
bs = [1,2]
if len(bs) > 4:
    print("True")
else:
    bs.append(3)
    print("False")
```
"""

code = """bs = [1,2]
if len(bs) > 4:
    print("True")
else:
    bs.append(3)
    print("False")
"""

session = get_new_session(code)

arg_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=1,
    lineno=1,
    col_offset=6,
    end_lineno=1,
    end_col_offset=7,
)

arg_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_literal=2,
    lineno=1,
    col_offset=8,
    end_lineno=1,
    end_col_offset=9,
)

bs_line_id = get_new_id()

bs_line = CallNode(
    id=bs_line_id,
    session_id=session.id,
    function_name="__build_list__",
    assigned_variable_name="bs",
    arguments=[arg_1.id, arg_2.id],
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=10,
)

# line 1

condition_line_id = get_new_id()
state_change_input_id = get_new_id()
state_change_output_id = get_new_id()

state_change_input = StateChangeNode(
    id=state_change_input_id,
    session_id=session.id,
    variable_name="bs",
    associated_node_id=condition_line_id,
    initial_value_node_id=bs_line_id,
    state_dependency_type=StateDependencyType.Read,
)

state_change_output = StateChangeNode(
    id=state_change_output_id,
    session_id=session.id,
    variable_name="bs",
    associated_node_id=condition_line_id,
    initial_value_node_id=bs_line_id,
    state_dependency_type=StateDependencyType.Write,
)

condition_line = ConditionNode(
    id=condition_line_id,
    session_id=session.id,
    input_state_change_nodes=[state_change_input_id],
    output_state_change_nodes=[state_change_output_id],
    lineno=2,
    col_offset=0,
    end_lineno=6,
    end_col_offset=18,
)

graph_with_conditionals = Graph(
    nodes=[
        condition_line,
        state_change_input,
        state_change_output,
        arg_1,
        arg_2,
        bs_line,
    ]
)
