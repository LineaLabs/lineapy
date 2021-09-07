from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    ArgumentNode,
    CallNode,
    Library,
)

from tests.util import get_new_id, get_new_session

import_code = "from math import pow as power, sqrt as root"
import_body_code = "a = power(5, 2)\nb = root(a)"

code = """from math import pow as power, sqrt as root
a = power(5, 2)\nb = root(a)
"""

math_lib = Library(id=get_new_id(), name="math", version="1", path="")

session = get_new_session(code, libraries=[math_lib])

import_math_node = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    library=math_lib,
    attributes={"power": "pow", "root": "sqrt"},
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=43,
)

arg_literal_id_1 = get_new_id()
arg_literal1 = ArgumentNode(
    id=arg_literal_id_1,
    session_id=session.id,
    positional_order=1,
    value_literal=5,
    lineno=2,
    col_offset=10,
    end_lineno=2,
    end_col_offset=11,
)

arg_literal_id_2 = get_new_id()
arg_literal2 = ArgumentNode(
    id=arg_literal_id_2,
    session_id=session.id,
    positional_order=2,
    value_literal=2,
    lineno=2,
    col_offset=13,
    end_lineno=2,
    end_col_offset=14,
)

line_2_id = get_new_id()

line_2 = CallNode(
    id=line_2_id,
    session_id=session.id,
    function_name="power",
    function_module=import_math_node.id,
    assigned_variable_name="a",
    arguments=[arg_literal_id_1, arg_literal_id_2],
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=15,
)

arg_a = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=line_2_id,
    lineno=3,
    col_offset=9,
    end_lineno=3,
    end_col_offset=10,
)

line_3_id = get_new_id()
line_3 = CallNode(
    id=line_3_id,
    session_id=session.id,
    function_name="root",
    function_module=import_math_node.id,
    assigned_variable_name="b",
    arguments=[arg_a.id],
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=11,
)

graph_with_import = Graph(
    [arg_literal1, arg_literal2, arg_a, import_math_node, line_2, line_3]
)
