from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Iterable, List, NewType, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict


class SessionType(Enum):
    """
    Session types allow the tracer to know what to expect
    - JUPYTER: the tracer need to progressively add more nodes to the graph
    - SCRIPT: the easiest case, run everything until the end
    """

    JUPYTER = 1
    SCRIPT = 2


"""
Following are the types used to construct the Linea IR. These should be fairly
  stable as changing them will likely result in major refactor.

You can find extensive examples in tests/stub_data.

The orm_mode allows us to use from_orm to convert ORM 
  objects to pydantic objects
"""


# Use a NewType instead of a string so that we can look at annotations of
# fields in pydantic models that use this to differentiate between strings and
# IDs when pretty printing
LineaID = NewType("LineaID", str)


class SessionContext(BaseModel):
    """
    Each trace of a script/notebook is a "Session".

    :param working_directory: captures where the code ran by the user

    """

    id: LineaID  # populated on creation by uuid.uuid4()
    environment_type: SessionType
    python_version: str
    creation_time: datetime.datetime
    working_directory: str  # must be passed in for now
    session_name: Optional[str] = None
    user_name: Optional[str] = None
    # The ID of the corresponding execution
    execution_id: LineaID

    class Config:
        orm_mode = True


class NodeType(Enum):
    Node = auto()
    CallNode = auto()
    LiteralNode = auto()
    ImportNode = auto()
    LookupNode = auto()
    MutateNode = auto()
    GlobalNode = auto()
    IfNode = auto()
    ElseNode = auto()


class LiteralType(Enum):
    String = auto()
    Integer = auto()
    Float = auto()
    Boolean = auto()
    NoneType = auto()
    Ellipsis = auto()
    Bytes = auto()


class ValueType(Enum):
    """
    Lower case because the API with the frontend assume the characters "chart"
    exactly as is.
    """

    # [TODO] Rename (need coordination with linea-server):
    # - `dataset` really is a table
    # - `value` means its a literal  (e.g., int/str)

    chart = 1
    array = 2
    dataset = 3
    code = 4
    value = 5  # includes int, string, bool


class NodeValue(BaseModel):
    node_id: LineaID
    # A pointer to the current execution
    execution_id: LineaID
    value: str
    value_type: Optional[ValueType]

    start_time: datetime.datetime
    end_time: datetime.datetime

    class Config:
        orm_mode = True


class Execution(BaseModel):
    """
    An execution is one session of running many nodes and recording their values.
    """

    id: LineaID
    timestamp: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class Artifact(BaseModel):
    """
    An artifact points to the value of a node during some execution.
    """

    node_id: LineaID
    execution_id: LineaID

    date_created: datetime.datetime
    name: str
    version: int

    class Config:
        orm_mode = True


class JupyterCell(BaseModel):
    # The execution number of the cell
    # https://nbformat.readthedocs.io/en/latest/format_description.html#code-cells
    execution_count: int
    # The session context ID for this execution
    session_id: LineaID


SourceCodeLocation = Union[Path, JupyterCell]


class SourceCode(BaseModel):
    """
    The source code of the code that was executed.
    """

    id: LineaID
    code: str
    location: SourceCodeLocation

    class Config:
        orm_mode = True

    def __hash__(self) -> int:
        return hash((self.id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SourceCode):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: object) -> bool:
        """
        Returns true if the this source code comes before the other, only applies
        to Jupyter sources.

        It will return not implemented, if they are not from the same file
        or the same Jupyter session.
        """
        if not isinstance(other, SourceCode):
            return NotImplemented
        self_location = self.location
        other_location = other.location
        if isinstance(self_location, Path) and isinstance(
            other_location, Path
        ):
            # If they are of different files, we can't compare them
            if self_location != other_location:
                return NotImplemented
            # Otherwise, they are equal so not lt
            return False
        elif isinstance(self_location, JupyterCell) and isinstance(
            other_location, JupyterCell
        ):
            # If they are from different sessions, we cant compare them.
            if self_location.session_id != other_location.session_id:
                return NotImplemented
            # Compare jupyter cells first by execution count, then line number
            return (self_location.execution_count) < (
                other_location.execution_count
            )
        # If they are different source locations, we don't know how to compare
        assert type(self_location) == type(other_location)
        return NotImplemented


class SourceLocation(BaseModel):
    """
    The location of the original source.

    eventually we need to also be able to support fused locations, like MLIR:
    https://mlir.llvm.org/docs/Dialects/Builtin/#location-attributes
    but for now we just point at the original user source location.
    """

    lineno: int
    col_offset: int = Field(repr=False)
    end_lineno: int = Field(repr=False)
    end_col_offset: int = Field(repr=False)
    source_code: SourceCode = Field(repr=False)

    def __lt__(self, other: object) -> bool:
        """
        Returns true if the this source location comes before the other.

        It will return not implemented, if they are not from the same file
        or the same Jupyter session.
        """
        if not isinstance(other, SourceLocation):
            return NotImplemented
        source_code_lt = self.source_code < other.source_code
        # If they are different source locations, we don't know how to compare
        if source_code_lt == NotImplemented:
            return NotImplemented
        # Otherwise, if they are from the same source, compare by line number
        if self.source_code.location == other.source_code.location:
            return (self.lineno, self.col_offset) < (
                other.lineno,
                other.col_offset,
            )
        return source_code_lt

    class Config:
        orm_mode = True


class BaseNode(BaseModel):
    """
    Attributes
    ----------
    id: str
        string version of UUID, which we chose because
        we do not need to coordinate to make it unique
    lineno: int
        Record the position of the calls. Optional because it is not required by some nodes,
        such as side-effects (which do not correspond to a line of code).
    col_offset: int
        Record the position of the calls. Optional because it is not required by some nodes,
        such as side-effects (which do not correspond to a line of code).
    end_lino: int
        Record the position of the calls. Optional because it is not required by some nodes,
        such as side-effects (which do not correspond to a line of code).
    end_col_offsets: int
        Record the position of the calls. Optional because it is not required by some nodes,
        such as side-effects (which do not correspond to a line of code).
    control_dependency: Optional[LineaID]
        points to a ControlFlowNode which the generation of
        the current node is dependent upon. For example, in the snippet
        `if condition: l.append(0)`, the `append` instruction's execution depends
        on the condition being true or not, hence the MutateNode corresponding to
        the append instruction will have it's control_dependency field pointing
        to the IfNode of the condition. Refer to tracer.py for usage.

    `class Config`'s orm_mode allows us to use from_orm to convert ORM
    objects to pydantic objects
    """

    id: LineaID
    session_id: LineaID = Field(repr=False)  # refers to SessionContext.id
    node_type: NodeType = Field(NodeType.Node, repr=False)
    source_location: Optional[SourceLocation] = Field(repr=False)
    control_dependency: Optional[LineaID]

    class Config:
        orm_mode = True

    def __lt__(self, other: object) -> bool:
        """
        Sort nodes by line number and column, putting those without line numbers
        at the beginning.

        Used to break ties in topological node ordering.
        """
        if not isinstance(other, BaseNode):
            return NotImplemented

        if not other.source_location:
            return False
        if not self.source_location:
            return True

        return self.source_location < other.source_location

    def parents(self) -> Iterable[LineaID]:
        """
        Returns the parents of this node.
        """
        # Return control dependencies, which could exist for any node
        if self.control_dependency:
            yield self.control_dependency


class ImportNode(BaseNode):
    """
    Imported libraries.

    `version` and `package_name` are retrieved at runtime.
    `package_name` may be different from import name, see get_lib_package_version.

    These are optional because the info is acquired at runtime.

    ??? note

        This node is not actually used for execution (using `l_import` CallNodes),
        but more a decoration for metadata retrieval.
    """

    node_type: NodeType = NodeType.ImportNode
    name: str
    version: Optional[str] = None
    package_name: Optional[str] = None
    path: Optional[str] = None


class PositionalArgument(BaseModel):
    id: LineaID
    starred: bool = False


class KeywordArgument(BaseModel):
    key: str
    value: LineaID
    starred: bool = False


class CallNode(BaseNode):
    """
    Attributes
    ----------
    function_id: LineaID
        node containing the value of the function call, which
        could be from various places: (1) locally defined, (2) imported, and
        (3) magically existing, e.g. from builtins (`min`), or environment
        like `get_ipython`.
    value: Object
        value of the call result, filled at runtime. It may be cached
        by the data asset manager
    """

    node_type: NodeType = Field(NodeType.CallNode, repr=False)

    function_id: LineaID
    positional_args: List[PositionalArgument] = []
    keyword_args: List[KeywordArgument] = []

    # Mapping of global variables that need to be set to call this function
    global_reads: Dict[str, LineaID] = {}

    # TODO: add documentation
    implicit_dependencies: List[LineaID] = []

    def parents(self) -> Iterable[LineaID]:
        yield from super().parents()
        yield self.function_id
        yield from [node.id for node in self.positional_args]
        yield from [node.value for node in self.keyword_args]
        yield from self.global_reads.values()
        yield from self.implicit_dependencies


class LiteralNode(BaseNode):
    node_type: NodeType = Field(NodeType.LiteralNode, repr=False)
    value: Any


class LookupNode(BaseNode):
    """
    For unknown/undefined variables e.g. SQLcontext, get_ipython, int.
    """

    node_type = Field(NodeType.LookupNode, repr=False)
    name: str


class MutateNode(BaseNode):
    """
    Represents a mutation of a node's value.

    After a call mutates a node then later references to that node will
    instead refer to this mutate node.
    """

    node_type = Field(NodeType.MutateNode, repr=False)

    # Points to the original node that was mutated
    source_id: LineaID

    # Points to the CallNode that did the mutation
    call_id: LineaID

    def parents(self) -> Iterable[LineaID]:
        yield from super().parents()
        yield self.source_id
        yield self.call_id


class GlobalNode(BaseNode):
    """
    Represents a lookup of a global variable, that was set as a side effect
    in another node.
    """

    node_type = Field(NodeType.GlobalNode, repr=False)

    # The name of the variable to look up from the result of the call
    name: str

    # Points to the call node that updated the global
    call_id: LineaID

    def parents(self) -> Iterable[LineaID]:
        yield from super().parents()
        yield self.call_id


class ControlFlowNode(BaseNode):
    """
    Represents a control flow node like `if`, `else`, `for`, `while`
    """

    node_type = Field(NodeType.Node, repr=False)

    # Points to the attached node
    # For `if` node, it will be an `else` node, for an `else` node it could be an `if` node, `while` node etc.
    companion_id: Optional[LineaID]

    # LiteralNode containing the code, if the block is not executed
    unexec_id: Optional[LineaID]

    def parents(self) -> Iterable[LineaID]:
        yield from super().parents()
        if self.companion_id:
            yield self.companion_id
        if self.unexec_id:
            yield self.unexec_id


class IfNode(ControlFlowNode):
    """
    Represents the `if` keyword
    """

    node_type = Field(NodeType.IfNode, repr=False)

    # Points to the call node which forms the expression to test
    test_id: LineaID

    def parents(self) -> Iterable[LineaID]:
        yield from super().parents()
        yield self.test_id


class ElseNode(ControlFlowNode):
    """
    Represents the `else` keyword
    """

    node_type = Field(NodeType.ElseNode, repr=False)

    # Points to the attached node
    # Could be a node corresponding to `if`, `for`, `while`, etc.
    # The definition here is used only for typing purposes, it will
    # automatically be included in super().parents()
    companion_id: LineaID


ControlNode = Union[IfNode, ElseNode]


# We can use this for more precise type definitions, to make sure we hit
# all the node cases
Node = Union[
    ImportNode,
    CallNode,
    LiteralNode,
    LookupNode,
    MutateNode,
    GlobalNode,
    ControlNode,
]


class AssignedVariable:
    """
    For local variables, this is the node that is assigned to.
    """

    node_id: LineaID
    assigned_variable: str


class WorkflowType(Enum):
    """
    Workflow types allow the `create_workflow` to know what to expect

    Attributes
    ----------
    SCRIPT: int
        the workflow is wrapped as a python script
    AIRFLOW: int
        the workflow is wrapped as an airflow dag
    DVC: int
        the workflow is wrapped as a DVC
    ARGO: int
        the workflow is wrapped as an Argo workflow dag
    KUBEFLOW: int
        the workflow is defined using Kubeflow's python SDK
    RAY: int
        the workflow is wrapped as a Ray DAG
    """

    SCRIPT = 1
    AIRFLOW = 2
    DVC = 3
    ARGO = 4
    KUBEFLOW = 5
    RAY = 6


FilePath = Union[str, Path]


class ARTIFACT_STORAGE_BACKEND(str, Enum):
    """
    Artifact storage backend
    """

    lineapy = "lineapy"
    mlflow = "mlflow"


class LineaArtifactDef(TypedDict):
    """
    Definition of an artifact, can extend new keys(user, project, ...)
    in the future.
    """

    artifact_name: str
    version: NotRequired[Optional[int]]


@dataclass
class LineaArtifactInfo:
    """
    Backend storage metadata for LineaPy
    """

    artifact_id: int
    name: str
    version: int
    execution_id: LineaID
    session_id: LineaID
    node_id: LineaID
    date_created: datetime.datetime
    storage_path: str
    storage_backend: ARTIFACT_STORAGE_BACKEND


@dataclass
class MLflowArtifactInfo:
    """
    Backend storage metadata for MLflow
    """

    id: int
    artifact_id: int
    tracking_uri: str
    registry_uri: Optional[str]
    model_uri: str
    model_flavor: str


class ArtifactInfo(TypedDict):
    """
    Artifact backend storage metadata

    Attributes
    ----------
    lineapy: LineaArtifactInfo
        storage backend for LineaPy
    mlflow: NotRequired[MLflowArtifactInfo]
        storage backend metadata for MLflow (only exists when the
        artifact is saved in MLflow)
    """

    lineapy: LineaArtifactInfo
    mlflow: NotRequired[MLflowArtifactInfo]
