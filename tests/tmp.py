import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id="39cb41e6-bbde-42b6-81e7-398733f9787e",
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(2021, 9, 29, 10, 12, 42, 741760),
    file_name="/private/var/folders/xn/05ktz3056kqd9n8frgd6236h0000gn/T/pytest-of-saul/pytest-480/test_alias_by_value0/source.py",
    code="a = 0\nb = a\na = 2\n",
    working_directory="/Users/saul/p/lineapy",
    libraries=[],
)
literal_1 = LiteralNode(
    id=literal_1.id,
    session_id=session.id,
    value=0,
)
literal_2 = LiteralNode(
    id=literal_2.id,
    session_id=session.id,
    value=2,
)
variable_1 = VariableNode(
    id=variable_1.id,
    session_id=session.id,
    source_node_id=literal_2.id,
    assigned_variable_name="a",
)
variable_2 = VariableNode(
    id=variable_2.id,
    session_id=session.id,
    source_node_id=literal_1.id,
    assigned_variable_name="a",
)
variable_3 = VariableNode(
    id=variable_3.id,
    session_id=session.id,
    source_node_id=variable_2.id,
    assigned_variable_name="b",
)
# Topological sort
literal_1, literal_2
variable_2, variable_1
variable_3
