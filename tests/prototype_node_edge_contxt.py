import uuid

import altair as alt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

alt.data_transformers.enable("json")
alt.renderers.enable("mimetype")

assets = pd.read_csv("ames_train_cleaned.csv")

sns.relplot(data=assets, x="Year_Built", y="SalePrice", size="Lot_Area")


def get_threshold():
    x = 1970
    return 1970


def is_new(col):
    return col > get_threshold()


assets["is_new"] = is_new(assets["Year_Built"])

clf = RandomForestClassifier(random_state=0)
y = assets["is_new"]
x = assets[["SalePrice", "Lot_Area", "Garage_Area"]]

clf.fit(x, y)
p = clf.predict([[100 * 1000, 10, 4]])
print("p value", p)

from lineapy.data.types import *


def get_new_id():
    return uuid.uuid4()


session = SessionContext(
    uuid=get_new_id(),
    session_name="housing",
    file_name="Housing Price.py",
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.now(),
)

alt_node_context = NodeContext(
    lines=(1, 1), columns=(1, 21), execution_time=datetime.now()
)
alt_node = ImportNode(
    name="alt",
    uuid=get_new_id(),
    code="import altair as alt",
    session_id=session.uuid,
    context=alt_node_context,
    library_name="altair",
    alias="alt",
    version="1.0",
)

pd_node_context = NodeContext(
    lines=(2, 2), columns=(1, 20), execution_time=datetime.now()
)
pd_node = ImportNode(
    name="pd",
    uuid=get_new_id(),
    code="import pandas as pd",
    session_id=session.uuid,
    context=pd_node_context,
    library_name="pandas",
    alias="pd",
    version="1.20",
)

sns_node_context = NodeContext(
    lines=(3, 3), columns=(1, 22), execution_time=datetime.now()
)
sns_node = ImportNode(
    name="sns",
    uuid=get_new_id(),
    code="import seaborn as sns",
    session_id=session.uuid,
    context=sns_node_context,
    library_name="seaborn",
    alias="sns",
    version="2.2",
)

rf_node_context = NodeContext(
    lines=(4, 4), columns=(1, 52), execution_time=datetime.now()
)
rf_node = ImportNode(
    name="RandomForestClassifier",
    uuid=get_new_id(),
    code="from sklearn.ensemble import RandomForestClassifier",
    session_id=session.uuid,
    context=rf_node_context,
    library_name="RandomForestClassifier",
    version="2.3",
)
lookup = {
    "alt": alt_node,
    "pd": pd_node,
    "sns": sns_node,
    "RandomForestClassifier": rf_node,
}

# Altair setup
dt_node_context = NodeContext(
    lines=(6, 6), columns=(1, 22), execution_time=datetime.now()
)
dt_node = Node(
    name="_auto_attr_0",
    uuid=get_new_id(),
    code="alt.data_transformers",
    session_id=session.uuid,
    context=dt_node_context,
)

edge1 = DirectedEdge(source_node_id=alt_node.id, sink_node_id=dt_node.id)

enable_node_context = NodeContext(
    lines=(6, 6), columns=(22, 37), execution_time=datetime.now()
)
enable_node = Node(
    name="_auto_call_0",
    uuid=get_new_id(),
    code=".enable('json')",
    session_id=session.uuid,
    context=enable_node_context,
)

edge2 = DirectedEdge(source_node_id=dt_node.id, sink_node_id=enable_node.id)

render_node_context = NodeContext(
    lines=(7, 7), columns=(1, 14), execution_time=datetime.now()
)
render_node = Node(
    name="_auto_attr_1",
    uuid=get_new_id(),
    code="alt.renderers",
    session_id=session.uuid,
    context=render_node_context,
)

edge3 = DirectedEdge(source_node_id=alt_node.id, sink_node_id=render_node.id)

enable2_node_context = NodeContext(
    lines=(7, 7), columns=(14, 33), execution_time=datetime.now()
)
enable2_node = Node(
    name="_auto_call_1",
    uuid=get_new_id(),
    code=".enable('mimetype')",
    session_id=session.uuid,
    context=enable2_node_context,
)

edge4 = DirectedEdge(source_node_id=render_node.id, sink_node_id=enable2_node.id)

stub_mutation_node = Node(
    name="alt_1", uuid=get_new_id(), code="", session_id=session.uuid
)

edge5 = DirectedEdge(source_node_id=enable_node.id, sink_node_id=stub_mutation_node.id)

edge6 = DirectedEdge(source_node_id=enable2_node.id, sink_node_id=stub_mutation_node.id)

lookup: Any = {
    "alt": stub_mutation_node,
    "pd": pd_node,
    "sns": sns_node,
    "RandomForestClassifier": rf_node,
}

assets_node_context = NodeContext(
    lines=(9, 9), columns=(1, 47), execution_time=datetime.now()
)
assets_node = CallNode(
    name="assets",
    uuid=get_new_id(),
    code=".read_csv('ames_train_cleaned.csv')",
    session_id=session.uuid,
    value=assets,
    context=assets_node_context,
)

edge7 = DirectedEdge(source_node_id=pd_node.id, sink_node_id=assets_node.id)

plot_node_context = NodeContext(
    lines=(11, 12), columns=(1, 60), execution_time=datetime.now()
)
plot_node = Node(
    name="_auto_call_2",
    uuid=get_new_id(),
    code='sns.relplot(data=assets,\nx="Year_Built", y="SalePrice", size="Lot_Area")',
    session_id=session.uuid,
    context=plot_node_context,
)

lookup: Any = {
    "alt": stub_mutation_node,
    "pd": pd_node,
    "sns": sns_node,
    "RandomForestClassifier": rf_node,
    "assets": assets_node,
}

edge8 = DirectedEdge(source_node_id=sns_node.id, sink_node_id=plot_node.id)
egde9 = DirectedEdge(source_node_id=assets_node.id, sink_node_id=plot_node.id)

# Function definitions
# Currently assumes pure functions
threshold_node_context = NodeContext(
    lines=(15, 16), columns=(1, 16), execution_time=datetime.now()
)
threshold_node = Node(
    name="get_threshold",
    uuid=get_new_id(),
    code="def get_threshold():\n    return 1970",
    session_id=session.uuid,
    value=get_threshold,
    context=threshold_node_context,
)
