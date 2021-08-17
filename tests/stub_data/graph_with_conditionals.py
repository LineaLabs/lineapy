from datetime import datetime

from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    ArgumentNode,
    CallNode,
    DirectedEdge,
    LiteralAssignNode,
    SessionContext,
    SessionType,
    ConditionNode,
    StateChangeNode,
)

from tests.util import get_new_id

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

session = SessionContext(
    uuid=get_new_id(),
    file_name="testing.py",
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.now(),
)

bs_line_id = get_new_id()

bs_line = LiteralAssignNode(
    id=bs_line_id,
    session_id=session.uuid,
    code="bs = [1,2]",
    assigned_variable_name="bs",
    value=[1, 2],
)

# line 1

condition_line_id = get_new_id()
state_change_id = get_new_id()

state_change = StateChangeNode(
    id=state_change_id, 
    session_id=session.uuid, 
    variable_name="bs", 
    associated_node_id=condition_line_id, 
    initial_value_node_id=bs_line_id,
)

condition_line = ConditionNode(
    id=condition_line_id,
    session_id=session.uuid,
    code="""if len(bs) > 4:\n\tprint("True")\nelse:\n\tbs.append(3)\n\tprint("False")""",
    dependent_variables_in_predicate=[bs_line_id],
    state_change_nodes=[state_change_id],
)

e_bs_to_cond = DirectedEdge(source_node_id=bs_line_id, sink_node_id=condition_line_id)

graph_with_conditionals = Graph(nodes=[bs_line, condition_line, state_change], edges=[e_bs_to_cond])
