from lineapy.data.graph import Graph
from tests.util import get_new_id
from tests.stub_data.simple_graph import session
from lineapy.data.types import LiteralAssignNode, VariableAliasNode

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
    session_id=session.uuid,
    code="a = 0",
    assigned_variable_name="a",
    value=0,
)

b_assign = VariableAliasNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="b = a",
    assigned_variable_name="b",
    source_variable_id=a_assign.id,
)

# I don't think we need to link this to the previous one?
# @dorx can you think of a case when this would be?
a_mutate = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="a = 2",
    assigned_variable_name="a",
    value=2,
)

# TODO: @dhruv please help complete
graph_with_alias_by_value = Graph([])


"""
a = [1,2,3]
b = a
a.append(4)
s = sum(b)
"""

# @dhruv please fill out the rest
# let me know if anything is not clear

graph_with_alias_by_reference = Graph([])
