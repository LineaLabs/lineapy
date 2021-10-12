from dataclasses import dataclass, field
from typing import Callable, Union


@dataclass(frozen=True)
class PositionalArg:
    index: int


@dataclass(frozen=True)
class KeywordArg:
    name: str


@dataclass(frozen=True)
class Result:
    """
    The result of a function call, used to describe a View.
    """

    pass


@dataclass(frozen=True)
class View:
    """
    Represents that the viewer is mutated whenever the source is mutated.
    """

    source: Union[PositionalArg, KeywordArg, Result]
    viewer: Union[PositionalArg, KeywordArg, Result]


@dataclass(frozen=True)
class InspectFunctionResult:
    mutated: set[Union[PositionalArg, KeywordArg]] = field(default_factory=set)
    views: set[View] = field(default_factory=set)


def inspect_function(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    result: object,
) -> InspectFunctionResult:
    """
    Inspects a function and returns how calling it mutates the args/result and
    creates view relationships between them.
    """
    # TODO: add special casing for different functions
    # And then eventually probably try to specify most of it declaratively
    # Or infer from docstrings/names, definitions, etc.
    return InspectFunctionResult()
