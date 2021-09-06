from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
)
from tests.util import get_new_id, get_new_session

"""
The simple graph represents the execution of the following:

```
a = abs(-1)
```

Notes:
- we don't really need NodeContext for execution so we are skipping it for now
- the ids are kept constant so we can more easily reference the same values in a different file
"""

simple_graph_code = "a = abs(-1)"

session = get_new_session()

arg_literal_id = get_new_id()

arg_literal = ArgumentNode(
    id=arg_literal_id, session_id=session.id, positional_order=1, value_literal=-11
)

line_1_id = get_new_id()

line_1 = CallNode(
    id=line_1_id,
    session_id=session.id,
    code="a = abs(-1)",
    function_name="abs",
    assigned_variable_name="a",
    arguments=[arg_literal_id],
)

simple_graph = Graph([arg_literal, line_1])
