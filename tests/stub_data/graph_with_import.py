from datetime import datetime

from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode, 
    Library, 
    SessionContext, 
    SessionType,
)

from tests.util import get_new_id

"""

```
import pandas as pd
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
    code="import pandas as pd", 
    library=Library(
        name="pandas", 
        version="1", 
        path="/home/"
    ), 
    alias="pd"
)

import_graph = Graph([line_1])