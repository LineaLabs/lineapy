from lineapy.data.graph import Graph, DirectedEdge
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    ConditionNode,
    StateChangeNode,
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
    print("False)    
```
"""

session = get_new_session()

arg_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=1,
)

arg_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_literal=2,
)

bs_line_id = get_new_id()

bs_line = CallNode(
    id=bs_line_id,
    session_id=session.id,
    code="bs = [1,2]",
    function_name="__build_list__",
    assigned_variable_name="bs",
    arguments=[arg_1.id, arg_2.id],
)

# line 1

condition_line_id = get_new_id()
state_change_id = get_new_id()

state_change = StateChangeNode(
    id=state_change_id,
    session_id=session.id,
    variable_name="bs",
    associated_node_id=condition_line_id,
    initial_value_node_id=bs_line_id,
)

condition_line = ConditionNode(
    id=condition_line_id,
    session_id=session.id,
    code="""if len(bs) > 4:\n\tprint("True")\nelse:\n\tbs.append(3)\n\tprint("False")""",
    dependent_variables_in_predicate=[bs_line_id],
    state_change_nodes=[state_change_id],
)

e_bs_to_cond = DirectedEdge(source_node_id=bs_line_id, sink_node_id=condition_line_id)

graph_with_conditionals = Graph(
    nodes=[condition_line, state_change, arg_1, arg_2, bs_line]
)
