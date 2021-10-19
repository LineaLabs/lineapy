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
    """
    If the function is a bound method, this refers to the instance that was
    bound of the method.
    """

    pass


@dataclass(frozen=True)
class Result:
    """
    The result of a function call, used to describe a View.
    """

    pass


# A set of values which all potentiall refer to shared pointers
# So that if one is mutated, the rest might be as well.
BidirectionalView = list[
    Union[PositionalArg, KeywordArg, Result, BoundSelfOfFunction]
]


@dataclass(frozen=True)
class InspectFunctionResult:
    # These are stored as lists for easier construction, but semantically they
    # are frozensets. It is useful also to keep the mutated ordered, to have
    # deterministic creation of mutated node order, without having to sort.

    # A set of values which are mutated
    mutated: list[
        Union[PositionalArg, KeywordArg, BoundSelfOfFunction]
    ] = field(default_factory=list)
    # A set of views, each of which represent a set of values which share poitners
    views: list[BidirectionalView] = field(default_factory=list)


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
            mutated=[PositionalArg(0)],
            # The first arg is now a view of the value, if the first arg is muttable
            views=[[PositionalArg(2), PositionalArg(0)]]
            if not is_immutable(args[2])
            else [],
        )
    if function == operator.delitem:
        # delitem(dict, key)
        return InspectFunctionResult(
            # The first arg, the dict, is mutated
            mutated=[PositionalArg(0)],
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
                mutated=[BoundSelfOfFunction()],
                views=[[BoundSelfOfFunction(), Result()]],
            )
    # Note: Future functions might require normalizing the args/kwargs with
    # inspect.signature.bind(args, kwargs) first
    return InspectFunctionResult()


def imported_module(name: str) -> bool:
    """
    Returns true if we have imported this module before.
    """
    return name in sys.modules


def is_immutable(obj: object) -> bool:
    """
    Returns true if the object is immutable.
    """
    # Assume all hashable objects are immutable
    try:
        hash(obj)
    except Exception:
        return False
    return True
