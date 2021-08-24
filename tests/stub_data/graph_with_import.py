from datetime import datetime

from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    ArgumentNode,
    CallNode,
    DirectedEdge,
    Library,
    SessionContext,
    SessionType,
)

from tests.util import get_new_id

"""

```
from math import pow, sqrt
a = power(5, 2)
b = root(a)
```
"""

session = SessionContext(
    id=get_new_id(),
    file_name="testing.py",
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.now(),
)

line_1_id = get_new_id()

line_1 = ImportNode(
    id=line_1_id,
    session_id=session.id,
    code="from math import pow, sqrt as root",
    library=Library(name="math", version="1", path=""),
    attributes={"power": "pow", "root": "sqrt"},
)

arg_literal_id_1 = get_new_id()
arg_literal1 = ArgumentNode(
    id=arg_literal_id_1, session_id=session.id, positional_order=1, value_literal=5
)

arg_literal_id_2 = get_new_id()
arg_literal2 = ArgumentNode(
    id=arg_literal_id_2, session_id=session.id, positional_order=1, value_literal=2
)

line_2_id = get_new_id()

line_2 = CallNode(
    id=line_2_id,
    session_id=session.id,
    code="power(5, 2)",
    function_name="power",
    function_module=line_1_id,
    assigned_variable_name="a",
    arguments=[arg_literal_id_1, arg_literal_id_2],
)

e2 = DirectedEdge(source_node_id=line_1_id, sink_node_id=line_2_id)

arg_a_id = get_new_id()

arg_a = ArgumentNode(
    id=arg_a_id, session_id=session.id, positional_order=1, value_node_id=line_2_id
)

line_3_id = get_new_id()
line_3 = CallNode(
    id=line_3_id,
    session_id=session.id,
    code="root(a)",
    function_name="root",
    function_module=line_1_id,
    assigned_variable_name="b",
    arguments=[arg_a_id],
)

e3 = DirectedEdge(source_node_id=line_2_id, sink_node_id=line_3_id)

graph_with_import = Graph(
    [arg_literal1, arg_literal2, arg_a, line_1, line_2, line_3], [e2, e3]
)
