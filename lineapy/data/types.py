from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Any, Tuple, Optional, List, NewType, TypeVar

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
    uuid: UUID  # populated on creation by uuid.uuid4()
    session_name: str  # obtained from name in with tracking(session_name=...):
    environment_type: SessionType
    creation_time: datetime
    file_name: Optional[str] = None
    user_name: Optional[str] = None
    hardware_spec: Optional[HardwareSpec] = None
    libraries: Optional[List[Library]] = None


class NodeContext(BaseModel):
    lines: Tuple[int, int]
    columns: Tuple[int, int]
    execution_time: datetime
    cell_id: Optional[str] = None  # only applicable to Jupyter sessions


# NodeValue = TypeVar("NodeValue")
# NodeValue = NewType('NodeValue', Optional[Any])
NodeValue = Any
# Yifan note: something weird here about optional and NewType... https://github.com/python/mypy/issues/4580; tried to use TypeVar but also kinda weird. Seems hairy https://stackoverflow.com/questions/59360567/define-a-custom-type-that-behaves-like-typing-any

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
    uuid: UUID  # populated on creation by uuid.uuid4()
    session_id: UUID  # refers to SessionContext.uuid
    code: str
    node_type: NodeType = NodeType.Node
    value: Optional[NodeValue] = None  # raw value of the node
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
    source_node_id: UUID  # refers to Node.uuid
    sink_node_id: UUID  # refers to Node.uuid
