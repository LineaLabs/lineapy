from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
)
from tests.util import get_new_id, get_new_session

"""
The simple graph represents the execution of the following:

```
a = abs(-11)
```

Notes:
- we don't really need NodeContext for execution so we are skipping it for now
- the ids are kept constant so we can more easily reference the same values 
  in a different file
"""

simple_graph_code = "a = abs(-11)"

session = get_new_session(simple_graph_code)

arg_literal = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=-11,
    lineno=1,
    col_offset=8,
    end_lineno=1,
    end_col_offset=11,
)

line_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="abs",
    assigned_variable_name="a",
    arguments=[arg_literal.id],
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=12,
)

simple_graph = Graph([arg_literal, line_1], session)
