from lineapy.data.graph import Graph
from lineapy.data.types import (
    LiteralNode,
)
from tests.util import get_new_id, get_new_session

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

code = """a = 0
b = a
a = 2
"""

session = get_new_session(code)

a_assign = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    assigned_variable_name="a",
    value=0,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=5,
)

b_assign = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    assigned_variable_name="b",
    value_node_id=a_assign.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=5,
)

# I don't think we need to link this to the previous one?
# @dorx can you think of a case when this would be?
a_mutate = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    assigned_variable_name="a",
    value=2,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=5,
)

graph_with_alias_by_value = Graph(nodes=[a_assign, b_assign, a_mutate])
