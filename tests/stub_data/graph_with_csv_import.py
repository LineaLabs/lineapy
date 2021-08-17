from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    DataSourceNode,
    Library,
    ImportNode,
    SessionType,
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
session = get_new_session()


# Note that this python path is EXPLICTLY tracking Yifan's own version
#   We should be able to handle these edge cases, and if not, we need to
#     specify what the requirement implications are for the node gen API
import_pandas = ImportNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="import pandas as pd",
    library=Library(
        name="pandas",
        version="1.2.4",
        path="/Users/yifanwu/miniforge3/lib/python3.9/site-packages/pandas",
    ),
    attributes={"power": "pow", "root": "sqrt"},
)

simple_data_node = DataSourceNode(
    id=get_new_id(),
    session_id=session.uuid,
    storage_type=StorageType.LOCAL_FILE_SYSTEM,
    access_path=import_pandas.library.path,
)

literal_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_literal="simple_data.csv",
)

read_csv_call = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="pd.read_csv('simple_data.csv')",
    function_name="read_csv",
    function_module=import_pandas.id,
    arguments=[literal_node],
)

col_name_literal = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_literal="a",
)

access_a_colum = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="df['a']",
    function_name="__getitem__",  # @dhruv this is a built in method, not sure if we need to add a module here
    arguments=[col_name_literal],
)

sum_call = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    function_name="sum",
    function_module=access_a_colum.id,
    assigned_variable_name="s",
)

# @Dhruv TODO create edges

graph_with_csv_import = Graph(
    [import_pandas, simple_data_node, literal_node, read_csv_call]
)
