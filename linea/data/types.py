import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Tuple, Optional, List, NewType

from pydantic import BaseModel


class SessionType(Enum):
    JUPYTER = 1
    SCRIPT = 2


class HardwareSpec(BaseModel):
    # TODO: information about the machine the code is run on.
    pass


class Library(BaseModel):
    name: str
    version: str
    path: str


class SessionContext(BaseModel):
    uuid: uuid.UUID  # populated on creation by uuid.uuid4()
    session_name: str  # obtained from name in with tracking(session_name=...):
    environment_type: SessionType
    creation_time: datetime
    file_name: Optional[str] = None
    user_name: Optional[str] = None
    hardware_spec: Optional[HardwareSpec] = None
    libraries: List[Library] = None


class NodeContext(BaseModel):
    lines: Tuple[int, int]
    columns: Tuple[int, int]
    execution_time: datetime
    cell_id: Optional[str] = None  # only applicable to Jupyter sessions


NodeValue = NewType('NodeValue', Optional[Any])


class NodeType(Enum):
    Node = 1
    ArgumentNode = 2
    CallNode = 3
    FunctionNode = 4
    ConditionNode = 5
    LoopNode = 6
    WithNode = 7
    ImportNode = 8


class Node(BaseModel):
    name: str
    uuid: uuid.UUID  # populated on creation by uuid.uuid4()
    code: str
    session_id: uuid.UUID  # refers to SessionContext.uuid
    node_type: NodeType = NodeType.Node
    value: NodeValue = None  # raw value of the node
    context: Optional[NodeContext] = None


class ImportNode(Node):
    node_type: NodeType = NodeType.ImportNode
    library: Library
    alias: Optional[str] = None


class ArgumentNode(Node):
    node_type: NodeType = NodeType.ArgumentNode
    # TODO


class CallNode(Node):
    node_type: NodeType = NodeType.CallNode
    args: List[ArgumentNode]
    # TODO


class FunctionNode(Node):
    node_type: NodeType = NodeType.FunctionNode
    # TODO


class ConditionNode(Node):
    node_type: NodeType = NodeType.ConditionNode
    # TODO


class LoopNode(Node):
    node_type: NodeType = NodeType.LoopNode
    # TODO


class WithNode(Node):
    node_type: NodeType = NodeType.WithNode
    # TODO


class DirectedEdge(BaseModel):
    source_node_id: uuid.UUID  # refers to Node.uuid
    sink_node_id: uuid.UUID  # refers to Node.uuid
