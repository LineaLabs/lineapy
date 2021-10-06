from dataclasses import dataclass
import datetime
from enum import Enum
from math import inf
from typing import Any, NewType, Tuple, Optional, List, Dict
from pydantic import BaseModel


class SessionType(Enum):
    """
    Session types allow the tracer to know what to expect
    - JUPYTER: the tracer need to progressively add more nodes to the graph
    - SCRIPT: the easiest case, run everything until the end
    - STATIC: does doesn't actually invoke the Executor
    """

    JUPYTER = 1
    SCRIPT = 2
    STATIC = 3


class StorageType(Enum):
    LOCAL_FILE_SYSTEM = 1
    S3 = 2
    DATABASE = 3


"""
Following are the types used to construct the Linea IR. These should be fairly
  stable as changing them will likely result in major refactor.

You can find extensive examples in tests/stub_data.

The orm_mode allows us to use from_orm to convert ORM 
  objects to pydantic objects
"""


# Use a NewType instead of a string so that we can look at annotations of fields in pydantic models
# that use this to differentiate between strings and IDs when pretty printing
LineaID = NewType("LineaID", str)


@dataclass
class DirectedEdge:
    """
    `DirectedEdge` is only used by the Graph to constructure dependencies
      so that we can use `networkx` directly.
    """

    source_node_id: LineaID
    sink_node_id: LineaID


class HardwareSpec(BaseModel):
    # TODO: information about the machine the code is run on.
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
    """
    Each execution of a script/notebook is a "Session".
    :param working_directory: captures where the code ran by the user

    The session context object provides important metadata used by
    - executor to get the code from the syntax_dictionary
    - route to supply the frontend, e.g., user_name and creation_time

    TODO:
    - we should remove the dependency on the working_directory because
      its brittle
    """

    id: LineaID  # populated on creation by uuid.uuid4()
    environment_type: SessionType
    creation_time: datetime.datetime
    # making file name required since every thing runs from some file
    file_name: str
    code: str
    working_directory: str  # must be passed in for now
    session_name: Optional[str]  # TODO: add API for user
    user_name: Optional[str] = None
    hardware_spec: Optional[HardwareSpec] = None
    libraries: List[Library] = []

    class Config:
        orm_mode = True


class NodeContext(BaseModel):
    lines: Tuple[int, int]
    columns: Tuple[int, int]
    execution_duration: datetime.datetime
    cell_id: Optional[str] = None  # only applicable to Jupyter sessions

    class Config:
        orm_mode = True


NodeValueType = Any


class NodeType(Enum):
    Node = 1
    ArgumentNode = 2
    CallNode = 3
    LiteralNode = 4
    # FunctionDefinitionNode = 5
    # ConditionNode = 6
    # LoopNode = 7
    WithNode = 8
    ImportNode = 9
    StateChangeNode = 10
    DataSourceNode = 11
    VariableNode = 12
    ClassDefinitionNode = 13
    SideEffectsNode = 14
    LookupNode = 15


class LiteralType(Enum):
    String = 1
    Integer = 2
    Float = 3
    Boolean = 4


class ValueType(Enum):
    """
    Lower case because the API with the frontend assume the characters "chart"
      exactly as is.
    FIXME---rename (need coordination with linea-server):
    - really `dataset` is a table
    - `value` means its a literal  (e.g., int/str)
    """

    chart = 1
    array = 2
    dataset = 3
    code = 4
    value = 5  # includes int, string, bool


class NodeValue(BaseModel):
    node_id: LineaID
    version: int
    value: NodeValueType
    value_type: ValueType
    virtual: bool
    timestamp: datetime.datetime

    class Config:
        orm_mode = True


class Execution(BaseModel):
    artifact_id: LineaID
    version: str
    timestamp: Optional[datetime.datetime]
    execution_time: float

    class Config:
        orm_mode = True


class Artifact(BaseModel):
    """
    An artifact is simply an annotation on some existing graph node---the ID
      simply points to an existing ID.
    """

    id: LineaID
    date_created: float
    name: Optional[str]

    class Config:
        orm_mode = True


class Node(BaseModel):
    """
    - id: string version of UUID, which we chose because
        we do not need to coordinate to make it unique
    - lineno, col_offset, end_lino, end_col_offsets: these record the position
      of the calls. They are optional because it's not required some nodes,
      such as side-effects nodes, which do not correspond to a line of code.

    - `class Config`'s orm_mode allows us to use from_orm to convert ORM
    objects to pydantic objects
    """

    id: LineaID
    session_id: LineaID  # refers to SessionContext.id
    node_type: NodeType = NodeType.Node
    lineno: Optional[int]
    col_offset: Optional[int]
    end_lineno: Optional[int]
    end_col_offset: Optional[int]

    class Config:
        orm_mode = True

    def __lt__(self, other: object) -> bool:
        """
        Sort nodes by line number and column, putting those without line numbers
        at the begining.

        Used to break ties in topological node ordering.
        """
        if not isinstance(other, Node):
            return NotImplemented
        return (self.lineno or -1, self.col_offset or -1) < (
            other.lineno or -1,
            other.col_offset or -1,
        )


class SideEffectsNode(Node):
    """
    This is a class of nodes, and the following nodes inherits from it:
    - LoopNode
    - ConditionNode
    - FunctionDefinitionNode

    All side effect nodes are handled currently as a black box
      The tracer would look into the definition to construct the input/output
      changes.

    Entries
    - `output_state_change_nodes`: IDs of the nodes that are modified, e.g.,
       `def foo:\n    global a\n    a = 1`
    - `input_state_change_nodes`: the nodes that reads, e.g.,
       `a = 1\ndef foo:\n    print(a)`
    - `import_nodes`: modules required to run node code
    """

    output_state_change_nodes: Optional[List[LineaID]]
    input_state_change_nodes: Optional[List[LineaID]]
    import_nodes: Optional[List[LineaID]]


class ImportNode(Node):
    """
    Example 1: import pandas as pd---library: pandas
    Example 2: from math import ceil

    """

    node_type: NodeType = NodeType.ImportNode
    library: Library

    # TODO: These are currently not needed anymore for linking, since
    # we are calling call(getattr) on the ImportNode directly to get attributes.
    # dict key is alias, value is full name
    attributes: Optional[Dict[str, str]] = None
    alias: Optional[str] = None

    # run time value
    module: Any = None


class ArgumentNode(Node):
    """
    Each call may have arguments, and the arguments are stored in ArgumentNode
    Each argument could be
    - keyword or positional (hence the optional)
    - value_literal or a reference to an existing variable (via the ID)
    """

    node_type: NodeType = NodeType.ArgumentNode
    # Either keyword or positiona_order is required, but not both
    keyword: Optional[str] = None
    positional_order: Optional[int] = None
    value_node_id: Optional[LineaID] = None
    value_literal: Optional[Any] = None


class CallNode(Node):
    """
    - `function_id`: node containing the value of the function call, which
      could be from various places: (1) locally defined, (2) imported, and
      (3) magically existing, e.g. from builtins (`min`), or environment
      like `get_ipython`.
    - `value`: value of the call result, filled at runtime. It may be cached
      by the data asset manager
    """

    node_type: NodeType = NodeType.CallNode
    # These IDs point to argument nodes
    arguments: List[LineaID]
    function_id: LineaID
    # TODO: We can refactor the next three into one function_id
    # function_name: str
    # function_module: Optional[LineaID] = None
    # locally_defined_function_id: Optional[LineaID] = None
    # assigned_variable_name: Optional[str] = None
    value: Optional[NodeValueType] = None


class LiteralNode(Node):
    node_type: NodeType = NodeType.LiteralNode
    value: NodeValueType


class LookupNode(Node):
    """
    For unknown/undefined variables e.g. SQLcontext, get_ipython, int.
    """

    node_type = NodeType.LookupNode
    name: str
    value: Optional[Any]


# TODO: Rename to AssignmentNode?
class VariableNode(Node):
    """
    Supports the following cases
    ```
    > b
    > a = b
    ```
    `b` would be the `source_node_id` in both cases,
    and `a` is the `assigned_variable_id` in the second case.
    """

    node_type: NodeType = NodeType.VariableNode
    source_node_id: LineaID
    assigned_variable_name: str
    value: Optional[Any]  # loaded at run time


class StateDependencyType(Enum):
    Read = 1
    Write = 2


class StateChangeNode(Node):
    """
    This type of node is to capture the state changes caused by "black boxes"
      such as loops.
    Each "black box" SideEffectsNode will have two types of StateChangeNodes
      for each variable. One for the variables read, and one variables written
      to.
    The `state_dependency_type` is used in the Graph class
      (`get_parents_from_node`) to identify how to construct the dependencies
    """

    node_type: NodeType = NodeType.StateChangeNode
    variable_name: str
    # this could be call id or loop id, or any code blocks
    associated_node_id: LineaID
    # points to a node that represents the value of the node before the
    #   change (can be another state change node)
    initial_value_node_id: LineaID
    state_dependency_type: StateDependencyType
    value: Optional[NodeValueType]


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
    - Also the access_path should be assumed to be unrolled to an absolute path
      so that it is resilient to where the execution happens.
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
