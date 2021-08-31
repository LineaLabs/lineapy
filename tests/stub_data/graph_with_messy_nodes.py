from lineapy.data.graph import Graph
from lineapy.data.types import (
    LiteralAssignNode,
    Library,
    ImportNode,
    ArgumentNode,
    CallNode,
)
from tests.util import get_new_id, get_new_session


"""
```
a = 1
b = a + 2
c = 2
d = 4
e = d + a
f = a * b * c
```

# slice on f

```
a = 1
b = a + 2
c = 2
f = a * b * c
```
"""

operator_lib = Library(id=get_new_id(), name="operator", version="1", path="")

session = get_new_session(libraries=[operator_lib])

a_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.id,
    code="a = 1",
    assigned_variable_name="a",
    value=1,
)

operator_module = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="import operator",
    library=operator_lib,
)

a_argument_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=a_assign.id,
)

argument_node_2 = ArgumentNode(
    id=get_new_id(), session_id=session.id, positional_order=2, value_literal=2
)

b_assign = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="b = a + 2",
    function_name="add",
    function_module=operator_module.id,  # built in
    assigned_variable_name="b",
    arguments=[a_argument_node.id, argument_node_2.id],
)

c_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.id,
    code="c = 2",
    assigned_variable_name="c",
    value=2,
)

d_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.id,
    code="d = 4",
    assigned_variable_name="d",
    value=4,
)

a_argument_node_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=a_assign.id,
)

d_argument_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_node_id=d_assign.id,
)

e_assign = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="e = d + a",
    function_name="add",
    function_module=operator_module.id,  # built in
    assigned_variable_name="e",
    arguments=[a_argument_node_2.id, d_argument_node.id],
)

a_argument_node_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=a_assign.id,
)

b_argument_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_node_id=b_assign.id,
)

f_assign_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="f = a * b * c",
    function_name="mul",
    function_module=operator_module.id,  # built in
    assigned_variable_name="f",
    arguments=[a_argument_node_3.id, b_argument_node.id],
)

f_argument_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=f_assign_1.id,
)

c_argument_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_node_id=c_assign.id,
)

f_assign = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="f = a * b * c",
    function_name="mul",
    function_module=operator_module.id,  # built in
    assigned_variable_name="f",
    arguments=[f_argument_node.id, c_argument_node.id],
)

graph_with_messy_nodes = Graph(
    [
        a_assign,
        operator_module,
        a_argument_node,
        argument_node_2,
        b_assign,
        c_assign,
        d_assign,
        a_argument_node_2,
        d_argument_node,
        e_assign,
        a_argument_node_3,
        b_argument_node,
        f_assign_1,
        f_argument_node,
        c_argument_node,
        f_assign,
    ]
)


graph_sliced_by_var_f = Graph(
    [
        a_assign,
        operator_module,
        a_argument_node,
        argument_node_2,
        b_assign,
        c_assign,
        a_argument_node_3,
        b_argument_node,
        f_assign_1,
        f_argument_node,
        c_argument_node,
        f_assign,
    ]
)
