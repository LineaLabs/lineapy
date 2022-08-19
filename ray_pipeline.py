%load_ext lineapy
# pip install ray==2.0.0rc1
# RAY_STORAGE=file:///tmp/ray/workflow ray start --head

import lineapy
from lineapy.plugins.pipeline_writers import RayWorkflowPipelineWriter
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.graph_reader.node_collection import (
    NodeCollection,
    NodeCollectionType,
    NodeInfo,
)

x = 1 + 2
a = 2 + 1
y = x * 10 + a

lineapy.save(x, 'my_x')

lineapy.save(y, 'my_y')

z = x + 20 + a
lineapy.save(z, 'my_z')

x_artifact = lineapy.get('my_x')
y_artifact = lineapy.get('my_y')
z_artifact = lineapy.get('my_z')

# ac = ArtifactCollection(["my_x", "my_y", "my_z"], False, "pipeline", ".")
sa = SessionArtifacts([x_artifact, y_artifact, z_artifact])
writer = RayWorkflowPipelineWriter([sa], False, "pipeline", ".")
writer._write_dag()
