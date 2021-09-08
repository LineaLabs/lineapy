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
"""

code = """import pandas as pd
import matplotlib.pyplot as plt
from PIL.Image import open
df = pd.read_csv('simple_data.csv')
plt.imsave('simple_data.png', df)
img = open('simple_data.png')
"""

pandas_lib = Library(
    id=get_new_id(),
    name="pandas",
    version="1.2.4",
    path="/Users/yifanwu/miniforge3/lib/python3.9/site-packages/pandas",
)

plt_lib = Library(id=get_new_id(), name="matplotlib.pyplot", version="", path="")

img_lib = Library(id=get_new_id(), name="PIL.Image", version="", path="")

session = get_new_session(code, libraries=[pandas_lib, plt_lib, img_lib])

# Note that this python path is EXPLICTLY tracking Yifan's own version
#   We should be able to handle these edge cases, and if not, we need to
#     specify what the requirement implications are for the node gen API
import_pandas = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    library=pandas_lib,
    alias="pd",
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=19,
)

import_pyplot = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    library=plt_lib,
    alias="plt",
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=31,
)

import_pil = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    library=img_lib,
    attributes={"open": "open"},
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=26,
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
    lineno=4,
    col_offset=17,
    end_lineno=4,
    end_col_offset=34,
)

read_csv_call = CallNode(
    id=UUID("73e1d1eb-fb9c-4fd4-b2c5-760829917361"),
    session_id=session.id,
    function_name="read_csv",
    function_module=import_pandas.id,
    assigned_variable_name="df",
    arguments=[literal_node.id],
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=35,
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
    lineno=5,
    col_offset=11,
    end_lineno=5,
    end_col_offset=28,
)

df_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_node_id=read_csv_call.id,
    lineno=5,
    col_offset=30,
    end_lineno=5,
    end_col_offset=32,
)

savefig_call = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="imsave",
    function_module=import_pyplot.id,
    arguments=[savefig_arg.id, df_arg.id],
    lineno=5,
    col_offset=0,
    end_lineno=5,
    end_col_offset=33,
)

savefig_arg2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=img_data_node.id,
    lineno=6,
    col_offset=11,
    end_lineno=6,
    end_col_offset=28,
)

read_call = CallNode(
    id=UUID("87620b97-c86b-4931-ab89-9f36898caa57"),
    session_id=session.id,
    function_name="open",
    function_module=import_pil.id,
    assigned_variable_name="img",
    arguments=[savefig_arg2.id],
    lineno=6,
    col_offset=0,
    end_lineno=6,
    end_col_offset=29,
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
