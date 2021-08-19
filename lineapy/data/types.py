from datetime import datetime
from enum import Enum
from typing import Any, Tuple, Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel

# aliasing the ID type in case we chnage it later
LineaID = UUID


class SessionType(Enum):
    JUPYTER = 1
    SCRIPT = 2


class StorageType(Enum):
    LOCAL_FILE_SYSTEM = 1
    S3 = 2
    DATABASE = 3


class HardwareSpec(BaseModel):
    # TODO: information about the machine the code is run on.
    pass


class Library(BaseModel):
    name: str
    version: str
    path: str


class SessionContext(BaseModel):
    uuid: LineaID  # populated on creation by uuid.uuid4()
    environment_type: SessionType
    creation_time: datetime
    file_name: str  # making file name required since every thing runs from some file
    session_name: Optional[
        str
    ]  # obtained from name in with tracking(session_name=...):
    user_name: Optional[str] = None
    hardware_spec: Optional[HardwareSpec] = None
    libraries: Optional[List[Library]] = None


class NodeContext(BaseModel):
    lines: Tuple[int, int]
    columns: Tuple[int, int]
    execution_duration: datetime
    cell_id: Optional[str] = None  # only applicable to Jupyter sessions


# NodeValue = TypeVar("NodeValue")
# NodeValue = NewType('NodeValue', Optional[Any])
NodeValue = Any


# Yifan note: something weird here about optional and NewType... https://github.com/python/mypy/issues/4580; tried to use TypeVar but also kinda weird. Seems hairy https://stackoverflow.com/questions/59360567/define-a-custom-type-that-behaves-like-typing-any


class NodeType(Enum):
    Node = 1
    ArgumentNode = 2
    CallNode = 3
    LiteralAssignNode = 4
    FunctionDefinitionNode = 5
    ConditionNode = 6
    LoopNode = 7
    WithNode = 8
    ImportNode = 9
    StateChangeNode = 10
    DataSourceNode = 11
    VariableAliasNode = 12
    ClassDefinitionNode = 13


class Node(BaseModel):
    id: LineaID  # populated on creation by uuid.uuid4()
    session_id: LineaID  # refers to SessionContext.uuid
    node_type: NodeType = NodeType.Node
    context: Optional[NodeContext] = None


class SideEffectsNode(Node):
    code: str
    # keeping a list of state_change_nodes that we probably have to re-construct from the sql db.
    # will deprecate when storing graph in a relational db
    state_change_nodes: Optional[List[LineaID]]
    import_nodes: Optional[
        List[LineaID]
    ]  # modules required to run node code (ids point to ImportNode instances)


class ImportNode(Node):
    node_type: NodeType = NodeType.ImportNode
    code: str
    library: Library
    attributes: Optional[Dict[str, str]] = None  # key is alias, value is full name
    alias: Optional[str] = None
    module: Any = None


class ArgumentNode(Node):
    node_type: NodeType = NodeType.ArgumentNode
    keyword: Optional[str]
    positional_order: Optional[int]
    value_node_id: Optional[LineaID]
    value_literal: Optional[Any]
    value_pickled: Optional[str]


class CallNode(Node):
    """
    The locally_defined_function_id helps with slicing and the lineapy transformer and corresponding APIs would need to capture these info.
    """

    node_type: NodeType = NodeType.CallNode
    code: str
    arguments: List[ArgumentNode]
    function_name: str
    function_module: Optional[
        LineaID
    ]  # could reference an Import Node, or a class (which would be the result of a CallNode)
    locally_defined_function_id: Optional[LineaID]
    assigned_variable_name: Optional[str]
    # value of the result, filled at runtime
    # TODO: maybe we should create a new class to differentiate?
    #       this run time value also applies to StateChange.
    value: Optional[NodeValue] = None


class LiteralAssignNode(Node):
    node_type: NodeType = NodeType.LiteralAssignNode
    code: str
    assigned_variable_name: str
    value: NodeValue
    value_node_id: Optional[LineaID]


class VariableAliasNode(Node):
    """
    Y: We could in theory merge LiteralAssignNode and VariableAliasNode, but I'm not sure what the pro/con are and we can always refactor?
    """

    node_type: NodeType = NodeType.VariableAliasNode
    code: str
    source_variable_id: LineaID


class FunctionDefinitionNode(SideEffectsNode):
    """
    Note that like loops, FunctionDefinitionNode will also treat the function as a black box.
    See tests/stub_data for examples.
    """

    node_type: NodeType = NodeType.FunctionDefinitionNode
    function_name: str
    value: Optional[Any]  # loaded at run time

    # TODO: should we track if its an recursive function?


class ConditionNode(SideEffectsNode):
    node_type: NodeType = NodeType.ConditionNode

    dependent_variables_in_predicate: Optional[List[LineaID]]


class StateChangeNode(Node):
    """
    This type of node is to capture the state changes caused by "black boxes" such as loops.
    Later code need to reference the NEW id now modified.
    """

    node_type: NodeType = NodeType.StateChangeNode
    variable_name: str
    # this could be call id or loop id, or any code blocks
    associated_node_id: LineaID
    initial_value_node_id: LineaID  # points to a node that represents the value of the node before the change (can be another state change node)
    value: Optional[NodeValue]


class LoopEnterNode(SideEffectsNode):
    """
    We do not care about the intermeidate states, but rather just what state has changed. It's conceptually similar to representing loops in a more functional way (such as map and reduce).  We do this by treating the LoopNode as a node similar to "CallNode".
    """

    node_type: NodeType = NodeType.LoopNode
    # keeping a list of state_change_nodes that we probably have to re-construct from the sql db.
    state_change_nodes: Optional[
        List[LineaID]
    ]  # a list of variables that are used in loop
    import_nodes: Optional[List[LineaID]]  # a list of modules that are used in loop


# Not sure if we need the exit node, commenting out for now
# class LoopExitNode(Node):
#     node_type: NodeType = NodeType.LoopNode
#     pass


class DataSourceNode(Node):
    """
    - The goal of identifying data source node is that we can start associating them even if they are accessed in slightly different ways.
    - Possible data sources:
        - CSV/S3
        - DB
    - For now we are just going to deal with local file systems and not support DB. Will add in the future.
    - Also the access_path should be assumed to be unrolled, but it can be a LOCAL access path, which means that it alone is not re-produceable.
    """

    node_type: NodeType = NodeType.DataSourceNode
    storage_type: StorageType
    access_path: str  # e.g., "/Users/yifanwu/miniforge3/lib/python3.9/site-packages/pandas"
    name: Optional[str]  # user defined


class WithNode(Node):
    node_type: NodeType = NodeType.WithNode
    code: str
    # TODO


class DirectedEdge(BaseModel):
    """
    When we have `a = foo(), b = bar(a)`, should the edge be between bar and foo, with foo being the source, and bar being the sink.
    Yifan note: @dorx please review if this is what you had in mind
    """

    source_node_id: LineaID  # refers to Node.uuid
    sink_node_id: LineaID  # refers to Node.uuid
