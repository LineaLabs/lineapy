import operator
import sys
import types
from dataclasses import dataclass, field
from typing import Callable, Union


@dataclass(frozen=True)
class PositionalArg:
    index: int


@dataclass(frozen=True)
class KeywordArg:
    name: str


@dataclass(frozen=True)
class BoundSelfOfFunction:
    pass


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

    This dataclass is used as the return value for inspecting a function, to
    provide more explicit names and types for the results.
    """

    source: Union[PositionalArg, KeywordArg, Result, BoundSelfOfFunction]
    viewer: Union[PositionalArg, KeywordArg, Result, BoundSelfOfFunction]


@dataclass(frozen=True)
class InspectFunctionResult:
    mutated: set[
        Union[PositionalArg, KeywordArg, BoundSelfOfFunction]
    ] = field(default_factory=set)
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

    # TODO: We should probably not use use setitem, but instead get particular
    # __setitem__ for class so we can differentiate based on type more easily?
    if function == operator.setitem:
        # setitem(dict, key, value)
        return InspectFunctionResult(
            # The first arg, the dict, is mutated
            mutated={PositionalArg(0)},
            # The first arg is now a view of the value
            views={View(PositionalArg(2), PositionalArg(0))},
        )
    if function == operator.delitem:
        # delitem(dict, key)
        return InspectFunctionResult(
            # The first arg, the dict, is mutated
            mutated={PositionalArg(0)},
        )
    if imported_module("sklearn"):
        from sklearn.base import BaseEstimator

        if (
            isinstance(function, types.MethodType)
            and function.__name__ == "fit"
            and isinstance(function.__self__, BaseEstimator)
        ):
            # In res = clf.fit(x, y)
            # cff is mutated, and we say that the res and the clf
            # are views of each other, since mutating one will mutate the other
            # since they are the same object.
            return InspectFunctionResult(
                mutated={BoundSelfOfFunction()},
                views={
                    View(BoundSelfOfFunction(), Result()),
                    View(Result(), BoundSelfOfFunction()),
                },
            )
    # Note: Future functions might require normalizing the args/kwargs with
    # inspect.signature.bind(args, kwargs) first
    return InspectFunctionResult()


def imported_module(name: str) -> bool:
    """
    Returns true if we have imported this module before.
    """
    return name in sys.modules
