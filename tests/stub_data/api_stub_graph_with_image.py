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
import matplotlib.image as mpimg

df = pd.read_csv('simple_data.csv')
df.plot()
plt.savefig('foo.png')
img=mpimg.imread('foo.png')


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

image_lib = Library(id=get_new_id(), name="matplotlib.image", version="", path="")
session = get_new_session(libraries=[pandas_lib, plt_lib, image_lib])

# Note that this python path is EXPLICTLY tracking Yifan's own version
#   We should be able to handle these edge cases, and if not, we need to
#     specify what the requirement implications are for the node gen API
import_pandas = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="import pandas as pd",
    library=pandas_lib,
    alias="pd",
)

import_pyplot = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="import matplotlib.pyplot as plt",
    library=plt_lib,
    alias="plt",
)

import_image = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    code="import matplotlib.image as mpimg",
    library=image_lib,
    alias="mpimg",
)

simple_data_node = DataSourceNode(
    id=get_new_id(),
    session_id=session.id,
    storage_type=StorageType.LOCAL_FILE_SYSTEM,
    # access_path="./tests/stub_data/simple_data.csv",
    access_path="../../tests/stub_data/simple_data.csv",
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
    code="df = pd.read_csv('ames_train_cleaned.csv')",
    function_name="read_csv",
    function_module=import_pandas.id,
    assigned_variable_name="df",
    arguments=[literal_node.id],
)

plot_call = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="df.plot()",
    function_name="plot",
    function_module=read_csv_call.id,
    arguments=[],
)

savefig_arg = ArgumentNode(
    id=get_new_id(), session_id=session.id, positional_order=1, value_literal="foo.png"
)

savefig_call = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="plt.savefig('foo.png')",
    function_name="savefig",
    function_module=import_pyplot.id,
    arguments=[savefig_arg.id],
)


graph_with_csv_import = Graph(
    [
        import_pandas,
        import_pyplot,
        import_image,
        simple_data_node,
        literal_node,
        read_csv_call,
        plot_call,
        savefig_arg,
        savefig_call,
    ],
)
