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
from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
```
"""

session = SessionContext(
    uuid=get_new_id(),
    file_name="testing.py",
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.now(),
)

line_1_id = get_new_id()

line_1 = ImportNode(
    id=line_1_id, 
    session_id = session.uuid, 
    code="from math import pow, sqrt as root", 
    library=Library(
        name="math", 
        version="1", 
        path=""
    ),
    attributes=[("pow", "power"), ("sqrt", "root")]
)

arg_literal_id_1 = get_new_id()
arg_literal1 = ArgumentNode(id=arg_literal_id_1, session_id=session.uuid, code="5", positional_order=1, value_literal=5)

arg_literal_id_2 = get_new_id()
arg_literal2 = ArgumentNode(id=arg_literal_id_2, session_id=session.uuid, code="2", positional_order=1, value_literal=2)

line_2_id = get_new_id()

line_2 = CallNode(
    id=line_2_id,
    session_id=session.uuid,
    code="power(5, 2)",
    function_name="power",
    assigned_variable_name="a",
    arguments=[arg_literal1, arg_literal2],
)

e2 = DirectedEdge(source_node_id=line_1_id, sink_node_id=line_2_id)

arg_a_id = get_new_id()

arg_a = ArgumentNode(id=arg_a_id, session_id=session.uuid, code="a", positional_order=1, value_call_id=line_2_id)

line_3_id = get_new_id()
line_3 = CallNode(
    id=line_3_id,
    session_id=session.uuid,
    code="root(a)",
    function_name="root",
    assigned_variable_name="b",
    arguments=[arg_a],
)

e3 = DirectedEdge(source_node_id=line_2_id, sink_node_id=line_3_id)

graph_with_import = Graph([line_1, arg_literal1, arg_literal2, line_2, arg_a, line_3], [e2, e3])