from lineapy.data.graph import Graph
from lineapy.data.types import (
    LiteralAssignNode,
)
from tests.stub_data.simple_graph import session
from tests.util import get_new_id

"""
```
a = 0
b = a
a = 2
```

TODO: in our slicing test, we should make sure that getting the slice for b returns.

```
a = 0
b = a
```
"""

a_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.id,
    code="a = 0",
    assigned_variable_name="a",
    value=0,
)

b_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.id,
    code="b = a",
    assigned_variable_name="b",
    value_node_id=a_assign.id,
)

# I don't think we need to link this to the previous one?
# @dorx can you think of a case when this would be?
a_mutate = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.id,
    code="a = 2",
    assigned_variable_name="a",
    value=2,
)

graph_with_alias_by_value = Graph(nodes=[a_assign, b_assign, a_mutate])
