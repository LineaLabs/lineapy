from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    ArgumentNode,
    CallNode,
    DirectedEdge,
    LiteralAssignNode,
    SessionContext,
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

arg_literal_id_1 = get_new_id()
arg_literal1 = ArgumentNode(
    id=arg_literal_id_1,
    session_id=session.uuid,
    code="1",
    positional_order=0,
    value_literal=1,
)

arg_literal_id_2 = get_new_id()
arg_literal2 = ArgumentNode(
    id=arg_literal_id_2,
    session_id=session.uuid,
    code="2",
    positional_order=1,
    value_literal=2,
)

# line 1
# @dhruv FIXME: I can't seem to figure out how to create a list programmatically. Last time when we created the empty list, I was able to use the `operator.list` method but you might want to look into how to initialize it with existing values.
# I'm also open to having lists as literals, so we can use an ArgumentNode, but then we'd have to think about serializing and deserializing values. Please evaluate the two options

bs_line = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="bs = [1,2]",
    assigned_variable_name="bs",
    function_name="list",
    arguments=[arg_literal1, arg_literal2],
)

condition_line = ConditionNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="""if len(bs) > 4:\n    print("True")\nelse:    bs.append(3\n    print("False)""",
    dependent_variables_in_predicate=[bs_line.id],
)


state_change = StateChangeNode(variable_name="bs", associated_node_id=condition_line.id)

# TODO: @dhruv please help me add the edges
graph_with_conditionals = Graph(nodes=[bs_line, state_change], edges=[])
