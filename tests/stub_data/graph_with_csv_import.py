from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    DataSourceNode,
    Library,
    ImportNode,
    SessionType,
    StorageType,
    DirectedEdge,
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
pandas_lib = Library(
    name="pandas",
    version="1.2.4",
    path="/Users/yifanwu/miniforge3/lib/python3.9/site-packages/pandas",
)

session = get_new_session(libraries=[pandas_lib])

# Note that this python path is EXPLICTLY tracking Yifan's own version
#   We should be able to handle these edge cases, and if not, we need to
#     specify what the requirement implications are for the node gen API
import_pandas = ImportNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="import pandas as pd",
    library=pandas_lib,
    alias="pd",
)

literal_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_literal="./tests/ames_train_cleaned.csv",
)

read_csv_call = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="df = pd.read_csv('ames_train_cleaned.csv')",
    function_name="read_csv",
    function_module=import_pandas.id,
    assigned_variable_name="df",
    arguments=[literal_node],
)

simple_data_node = DataSourceNode(
    id=get_new_id(),
    session_id=session.uuid,
    storage_type=StorageType.LOCAL_FILE_SYSTEM,
    access_path=read_csv_call.arguments[0].value_literal,
)

col_name_literal = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_literal="Lot_Area",
)

access_a_column = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="df['a']",
    function_name="__getitem__",  # @dhruv this is a built in method, not sure if we need to add a module here
    function_module=read_csv_call.id,
    arguments=[col_name_literal],
)

sum_call = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="s = df['a'].sum()",
    arguments=[],
    function_name="sum",
    function_module=access_a_column.id,
    assigned_variable_name="s",
)

e_import_to_df = DirectedEdge(
    source_node_id=import_pandas.id, sink_node_id=read_csv_call.id
)
e_df_to_access_a = DirectedEdge(
    source_node_id=read_csv_call.id, sink_node_id=access_a_column.id
)
e_df_to_sum = DirectedEdge(source_node_id=access_a_column.id, sink_node_id=sum_call.id)

graph_with_csv_import = Graph(
    [
        import_pandas,
        simple_data_node,
        access_a_column,
        literal_node,
        read_csv_call,
        sum_call,
    ],
    [e_import_to_df, e_df_to_access_a, e_df_to_sum],
)
