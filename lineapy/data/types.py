from __future__ import annotations

import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Iterable, List, NewType, Optional, Union

from pydantic import BaseModel, Field


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

    - we should remove the dependency on the working_directory because
      its brittle
    """

    id: LineaID  # populated on creation by uuid.uuid4()
    environment_type: SessionType
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


class LiteralType(Enum):
    String = auto()
    Integer = auto()
    Float = auto()
    Boolean = auto()
    NoneType = auto()
    Ellipsis = auto()


class ValueType(Enum):
    """
    Lower case because the API with the frontend assume the characters "chart"
    exactly as is.

    TODO
    ----
    FIXME

    - rename (need coordination with linea-server):
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
    version: Optional[str]

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
    - id: string version of UUID, which we chose because
      we do not need to coordinate to make it unique
    - lineno, col_offset, end_lino, end_col_offsets: these record the position
      of the calls. They are optional because it's not required some nodes,
      such as side-effects nodes, which do not correspond to a line of code.

    - `class Config`'s orm_mode allows us to use from_orm to convert ORM
      objects to pydantic objects

    """

    id: LineaID
    session_id: LineaID = Field(repr=False)  # refers to SessionContext.id
    node_type: NodeType = Field(NodeType.Node, repr=False)
    source_location: Optional[SourceLocation] = Field(repr=False)

    class Config:
        orm_mode = True

    def __lt__(self, other: object) -> bool:
        """
        Sort nodes by line number and column, putting those without line numbers
        at the begining.

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
        # Make an empty generator by yielding from an empty list

        yield from []


class ImportNode(BaseNode):
    """
    Imported libraries.

    `version` and `package_name` are retrieved at runtime.
    `package_name` may be different from import name, see get_lib_package_version.
    Optional because of runtime info
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
    - `function_id`: node containing the value of the function call, which
      could be from various places: (1) locally defined, (2) imported, and
      (3) magically existing, e.g. from builtins (`min`), or environment
      like `get_ipython`.
    - `value`: value of the call result, filled at runtime. It may be cached
      by the data asset manager
    """

    node_type: NodeType = Field(NodeType.CallNode, repr=False)

    function_id: LineaID
    positional_args: List[PositionalArgument] = []
    keyword_args: List[KeywordArgument] = []

    # Mapping of global variables that need to be set to call this function
    global_reads: Dict[str, LineaID] = {}

    implicit_dependencies: List[LineaID] = []

    def parents(self) -> Iterable[LineaID]:
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
        yield self.call_id


# We can use this for more precise type definitions, to make sure we hit
# all the node cases
Node = Union[
    ImportNode, CallNode, LiteralNode, LookupNode, MutateNode, GlobalNode
]


class PipelineType(Enum):
    """
    Pipeline types allow the to_pipeline to know what to expect
    - SCRIPT : the pipeline is wrapped as a python script
    - AIRFLOW : the pipeline is wrapped as an airflow dag
    """

    SCRIPT = 1
    AIRFLOW = 2
