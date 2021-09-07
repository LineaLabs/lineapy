from uuid import UUID

from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    DataSourceNode,
    Library,
    ImportNode,
    StorageType,
)
from tests.util import get_new_id, get_new_session

"""
```python
import pandas as pd
df = pd.read_csv('simple_data.csv')
s = df['a'].sum()
```
This test also has method chaining, which is a good case
"""

code = """import pandas as pd
df = pd.read_csv('simple_data.csv')
s = df['a'].sum()
"""

pandas_lib = Library(
    id=get_new_id(),
    name="pandas",
    version="1.2.4",
    path="/Users/yifanwu/miniforge3/lib/python3.9/site-packages/pandas",
)

session = get_new_session(code, libraries=[pandas_lib])

# Note that this python path is EXPLICTLY tracking Yifan's own version
#   We should be able to handle these edge cases, and if not, we need to
#     specify what the requirement implications are for the node gen API
import_pandas = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    library=pandas_lib,
    alias="pd",
)

simple_data_node = DataSourceNode(
    id=get_new_id(),
    session_id=session.id,
    storage_type=StorageType.LOCAL_FILE_SYSTEM,
    # access_path="./tests/stub_data/simple_data.csv",
    access_path="tests/stub_data/simple_data.csv",
)

literal_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=simple_data_node.id,
)

read_csv_call = CallNode(
    id=UUID("e01d7a89-0d6d-474b-8119-b5f087cbd66e"),
    session_id=session.id,
    function_name="read_csv",
    function_module=import_pandas.id,
    assigned_variable_name="df",
    arguments=[literal_node.id],
)

col_name_literal = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal="a",
)

access_a_column = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="__getitem__",  # @dhruv this is a built in method, not sure if we need to add a module here
    function_module=read_csv_call.id,
    arguments=[col_name_literal.id],
)

sum_call = CallNode(
    id=UUID("ccebc2e9-d710-4943-8bae-947fa1492d7f"),
    session_id=session.id,
    arguments=[],
    function_name="sum",
    function_module=access_a_column.id,
    assigned_variable_name="s",
)

graph_with_csv_import = Graph(
    [
        access_a_column,
        import_pandas,
        simple_data_node,
        literal_node,
        read_csv_call,
        sum_call,
        col_name_literal,
    ],
)
