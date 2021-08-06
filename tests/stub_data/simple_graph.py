from datetime import datetime

from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    SessionContext,
    SessionType,
)
from ..util import get_new_id

"""
The simple graph represents the execution of the following:

```
a = abs(-1)
```

Notes:
- we don't really need NodeContext for execution so we are skipping it for now
- the UUIDs are kept constant so we can more easily reference the same values in a different file
"""

session = SessionContext(
    uuid=get_new_id(),
    file_name="testing.py",
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.now(),
)

arg_literal_id = get_new_id()

arg_literal = ArgumentNode(id=arg_literal_id, positional_order=1, value_literal=-1)

line_1_id = get_new_id()

line_1 = CallNode(
    id=line_1_id,
    session_id=session,
    function_name="abs",
    assigned_variable_name="a",
    arguments=[arg_literal],
)

simple_graph = Graph([line_1, arg_literal])
