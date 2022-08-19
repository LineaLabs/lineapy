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

# GENERATED CODE:
"""

import ray
import ray.workflow as workflow
import os
assert os.environ.get("RAY_ADDRESS") is not None
ray.init(address=os.environ["RAY_ADDRESS"])
workflow.init()
def get_my_x():
    x = 1 + 2
    return x

def get_a_for_artifact_my_y_and_downstream():
    a = 2 + 1
    return a

def get_my_y(a, x):
    y = x * 10 + a
    return y

def get_my_z(a, x):
    z = x + 20 + a
    return z

@ray.remote
def _ray_my_x(*args):
    inputs = {k: v for d in args for k, v in d.items()}
    rets = get_my_x(**inputs)
    outputs = ['x']
    if not isinstance(rets, (list, tuple)): rets = [rets]
    return dict(zip(outputs, rets))
_ray_my_x_node = _ray_my_x.bind()

@ray.remote
def _ray_a_for_artifact_my_y_and_downstream(*args):
    inputs = {k: v for d in args for k, v in d.items()}
    rets = get_a_for_artifact_my_y_and_downstream(**inputs)
    outputs = ['a']
    if not isinstance(rets, (list, tuple)): rets = [rets]
    return dict(zip(outputs, rets))
_ray_a_for_artifact_my_y_and_downstream_node = _ray_a_for_artifact_my_y_and_downstream.bind()

@ray.remote
def _ray_my_y(*args):
    inputs = {k: v for d in args for k, v in d.items()}
    rets = get_my_y(**inputs)
    outputs = ['y']
    if not isinstance(rets, (list, tuple)): rets = [rets]
    return dict(zip(outputs, rets))
_ray_my_y_node = _ray_my_y.bind(_ray_a_for_artifact_my_y_and_downstream_node, _ray_my_x_node)

@ray.remote
def _ray_my_z(*args):
    inputs = {k: v for d in args for k, v in d.items()}
    rets = get_my_z(**inputs)
    outputs = ['z']
    if not isinstance(rets, (list, tuple)): rets = [rets]
    return dict(zip(outputs, rets))
_ray_my_z_node = _ray_my_z.bind(_ray_a_for_artifact_my_y_and_downstream_node, _ray_my_x_node)

@ray.remote(**workflow.options(checkpoint=False))
def gather(*args):
    return {k: v for d in args for k, v in d.items()}

_dag = gather.bind(_ray_my_x_node,_ray_my_y_node,_ray_my_z_node)
workflow_id = os.environ.get("WORKFLOD_ID")
# if not set, random id will be generated.
# we might want:
# 1. pass workflow id with cli.
# 2. choose to resume or just start a new one.
print(ray.workflow.run(_dag, workflow_id))
"""
