from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

from lineapy.data.types import LineaID
from lineapy.instrumentation.annotation_spec import ExternalState


@dataclass(frozen=True)
class MutatedNode:
    """
    Represents that a node has been mutated.
    """

    # The node that was mutated, the source node
    pointer: ExecutorPointer


@dataclass
class ViewOfNodes:
    """
    Represents that a set of nodes are now "views" of each other, meaning that
    if any are mutated they all could be mutated.
    """

    # An ordered set
    pointers: List[ExecutorPointer]


@dataclass
class ImplicitDependencyNode:
    """
    Represents that the call node has an implicit dependency on another node.
    """

    pointer: ExecutorPointer


@dataclass
class AccessedGlobals:
    """
    Represents some global variables that were retireved or changed during this call.
    """

    retrieved: List[str]
    added_or_updated: List[str]


SideEffect = Union[
    MutatedNode, ViewOfNodes, AccessedGlobals, ImplicitDependencyNode
]
SideEffects = List[SideEffect]


@dataclass
class ID:
    id: LineaID


@dataclass
class Variable:
    name: str


# Instead of just passing back the linea ID for the side effect, we create
# a couple of different cases, to cover different things we might want to point
# to.
ExecutorPointer = Union[ID, Variable, ExternalState]
