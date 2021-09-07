from lineapy.data.graph import Graph, DirectedEdge
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    DataSourceNode,
    Library,
    ImportNode,
    StorageType,
)
from tests.util import get_new_id, get_new_session

from uuid import UUID

"""
```python
import pandas as pd
import matplotlib.pyplot as plt
from PIL.Image import open

df = pd.read_csv('simple_data.csv')
plt.imsave('simple_data.png', df)
img = open('simple_data.png')

```
This test also has method chaining, which is a good case
"""
pandas_lib = Library(
    id=get_new_id(),
    name="pandas",
    version="1.2.4",
    path="/Users/yifanwu/miniforge3/lib/python3.9/site-packages/pandas",
)

plt_lib = Library(id=get_new_id(), name="matplotlib.pyplot", version="", path="")

img_lib = Library(id=get_new_id(), name="PIL.Image", version="", path="")

session = get_new_session(libraries=[pandas_lib, plt_lib, img_lib])

# Note that this python path is EXPLICTLY tracking Yifan's own version
#   We should be able to handle these edge cases, and if not, we need to
#     specify what the requirement implications are for the node gen API
import_pandas = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="import pandas as pd",
    library=pandas_lib,
    alias="pd",
    line=0,
)

import_pyplot = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="import matplotlib.pyplot as plt",
    library=plt_lib,
    alias="plt",
    line=1,
)

import_pil = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="from PIL.Image import open",
    library=img_lib,
    attributes={"open": "open"},
    line=2,
)


simple_data_node = DataSourceNode(
    id=get_new_id(),
    session_id=session.id,
    storage_type=StorageType.LOCAL_FILE_SYSTEM,
    # access_path="./tests/stub_data/simple_data.csv",
    access_path="tests/stub_data/simple_data.csv",
    line=3,
)

literal_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=simple_data_node.id,
    line=3,
)

read_csv_call = CallNode(
    id=UUID("73e1d1eb-fb9c-4fd4-b2c5-760829917361"),
    session_id=session.id,
    code="df = pd.read_csv('simple_data.csv')",
    function_name="read_csv",
    function_module=import_pandas.id,
    assigned_variable_name="df",
    arguments=[literal_node.id],
    line=3,
)

img_data_node = DataSourceNode(
    id=get_new_id(),
    session_id=session.id,
    storage_type=StorageType.LOCAL_FILE_SYSTEM,
    # access_path="./tests/stub_data/simple_data.csv",
    access_path="simple_data.png",
    line=4,
)

savefig_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=img_data_node.id,
    line=4,
)

df_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_node_id=read_csv_call.id,
    line=4,
)

savefig_call = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="plt.imsave('simple_data.png', df)",
    function_name="imsave",
    function_module=import_pyplot.id,
    arguments=[savefig_arg.id, df_arg.id],
    line=4,
)

savefig_arg2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=img_data_node.id,
    line=5,
)

read_call = CallNode(
    id=UUID("87620b97-c86b-4931-ab89-9f36898caa57"),
    session_id=session.id,
    code="img = open('simple_data.png')",
    function_name="open",
    function_module=import_pil.id,
    assigned_variable_name="img",
    arguments=[savefig_arg2.id],
    line=5,
)


graph_with_basic_image = Graph(
    [
        import_pandas,
        import_pyplot,
        import_pil,
        simple_data_node,
        literal_node,
        read_csv_call,
        savefig_arg,
        df_arg,
        savefig_call,
        savefig_arg2,
        img_data_node,
        read_call,
    ],
)
