from datetime import datetime
from enum import Enum
from typing import Any, Tuple, Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel

# aliasing the ID type in case we change it later
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

    # note: this is specific to Pydantic
    # orm_mode allows us to use from_orm to convert ORM objects to pydantic objects
    class Config:
        orm_mode = True


class Library(BaseModel):
    id: LineaID
    name: str
    version: Optional[str] = None  # optional because retrieved at runtime
    path: Optional[str] = None  # optional because retrieved at runtime

    class Config:
        orm_mode = True


class SessionContext(BaseModel):
    id: LineaID  # populated on creation by uuid.uuid4()
    environment_type: SessionType
    creation_time: datetime
    file_name: str  # making file name required since every thing runs from some file
    session_name: Optional[
        str
    ]  # obtained from name in with tracking(session_name=...):
    user_name: Optional[str] = None
    hardware_spec: Optional[HardwareSpec] = None
    libraries: Optional[List[Library]] = None
    code: str

    class Config:
        orm_mode = True


class NodeContext(BaseModel):
    lines: Tuple[int, int]
    columns: Tuple[int, int]
    execution_duration: datetime
    cell_id: Optional[str] = None  # only applicable to Jupyter sessions

    class Config:
        orm_mode = True


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
    SideEffectsNode = 14


class LiteralType(Enum):
    String = 1
    Integer = 2
    Float = 3
    Boolean = 4


CHART_TYPE = "chart"
ARRAY_TYPE = "array"
DATASET_TYPE = "dataset"
CODE_TYPE = "code"
VALUE_TYPE = "value"


class Execution(BaseModel):
    artifact_id: LineaID
    version: str
    timestamp: Optional[datetime]
    execution_time: int

    class Config:
        orm_mode = True


class Artifact(BaseModel):
    id: LineaID
    context: LineaID
    value_type: str
    name: Optional[str]
    project: Optional[str]
    description: Optional[str]
    date_created: str

    class Config:
        orm_mode = True


class Node(BaseModel):
    id: LineaID  # populated on creation by uuid.uuid4()
    session_id: LineaID  # refers to SessionContext.id
    node_type: NodeType = NodeType.Node
    # these identifiers are Optional because there are some
    #   kinds of nodes which are implicitly defined,
    #   including ImportNodes where the import is the operator module
    lineno: Optional[int]
    col_offset: Optional[int]
    end_lineno: Optional[int]
    end_col_offset: Optional[int]

    # context: Optional[NodeContext] = None

    # note: this is specific to Pydantic
    #   orm_mode allows us to use from_orm to convert ORM objects to
    #   pydantic objects
    class Config:
        orm_mode = True


class SideEffectsNode(Node):
    # keeping a list of state_change_nodes that we probably have to
    #   re-construct from th›e sql db.
    # will deprecate when storing graph in a relational db
    state_change_nodes: Optional[List[LineaID]]

    # modules required to run node code (ids point to ImportNode instances)
    import_nodes: Optional[List[LineaID]]


class ImportNode(Node):
    """
    Example 1: import pandas as pd---library: pandas
    Example 2: from math import ceil

    """

    node_type: NodeType = NodeType.ImportNode
    library: Library
    # dict key is alias, value is full name
    attributes: Optional[Dict[str, str]] = None
    alias: Optional[str] = None
    # run time value
    module: Any = None


class ArgumentNode(Node):
    node_type: NodeType = NodeType.ArgumentNode
    keyword: Optional[str] = None
    positional_order: Optional[int] = None
    value_node_id: Optional[LineaID] = None
    value_literal: Optional[Any] = None


class CallNode(Node):
    """
    The locally_defined_function_id helps with slicing and the lineapy
    transformer and corresponding APIs would need to capture these info.
    NOTE: could reference an Import Node, or a class,
      which would be the result of a CallNode.
    """

    node_type: NodeType = NodeType.CallNode
    arguments: List[LineaID]
    function_name: str
    function_module: Optional[LineaID] = None
    locally_defined_function_id: Optional[LineaID] = None
    assigned_variable_name: Optional[str] = None
    # value of the result, filled at runtime
    # TODO: maybe we should create a new class to differentiate?
    #       this run time value also applies to StateChange.
    value: Optional[NodeValue] = None


class LiteralAssignNode(Node):
    node_type: NodeType = NodeType.LiteralAssignNode
    assigned_variable_name: str
    value: NodeValue
    value_node_id: Optional[LineaID]


class VariableAliasNode(Node):

    node_type: NodeType = NodeType.VariableAliasNode
    source_variable_id: LineaID


class FunctionDefinitionNode(SideEffectsNode):
    """
    Note that like loops, FunctionDefinitionNode will also treat the
      function as a black box.
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
    This type of node is to capture the state changes caused by "black boxes"
      such as loops. Later code need to reference the NEW id now modified.
    """

    node_type: NodeType = NodeType.StateChangeNode
    variable_name: str
    # this could be call id or loop id, or any code blocks
    associated_node_id: LineaID
    # points to a node that represents the value of the node
    # before the change (can be another state change node)
    initial_value_node_id: LineaID
    value: Optional[NodeValue]


class LoopNode(SideEffectsNode):
    """
    We do not care about the intermeidate states, but rather just what state has
      changed. It's conceptually similar to representing loops in a more
      functional way (such as map and reduce).  We do this by treating
      the LoopNode as a node similar to "CallNode".
    """

    node_type: NodeType = NodeType.LoopNode


class DataSourceNode(Node):
    """
    NOTE:
    - The goal of identifying data source node is that we can start associating
      them even if they are accessed in slightly different ways.
    - Possible data sources:
        - CSV/S3
        - DB
    - For now we are just going to deal with local file systems and not
      support DB. Will add in the future.
    - Also the access_path should be assumed to be unrolled,
      but it can be a LOCAL access path, which means that it
      alone is not re-produceable.

    FIXME: this is currently conflated with all file paths, including
      generated files
    """

    node_type: NodeType = NodeType.DataSourceNode
    storage_type: StorageType
    access_path: str
    name: Optional[str]  # user defined


class WithNode(Node):
    node_type: NodeType = NodeType.WithNode
    # TODO


class DirectedEdge(BaseModel):
    """
    When we have `a = foo(), b = bar(a)`, should the edge be between bar and foo, with foo being the source, and bar being the sink.
    Yifan note: @dorx please review if this is what you had in mind
    """

    source_node_id: LineaID  # refers to Node.uuid
    sink_node_id: LineaID  # refers to Node.uuid

    class Config:
        orm_mode = True
