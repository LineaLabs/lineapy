import operator
import sys
import types
from dataclasses import dataclass
from typing import Callable, Iterable, Union


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


Pointer = Union[PositionalArg, KeywordArg, Result, BoundSelfOfFunction]


class ViewOfPointers:
    """
    A set of values which all potentially refer to shared pointers
    So that if one is mutated, the rest might be as well.
    """

    # They are unique, like a set, but ordered for deterministc behaviour
    pointers: list[Pointer]

    def __init__(self, *xs: Pointer) -> None:
        self.pointers = list(xs)


@dataclass(frozen=True)
class MutatedPointer:
    """
    A value that is mutated when the function is called
    """

    pointer: Pointer


def inspect_function(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    result: object,
) -> Iterable[Union[ViewOfPointers, MutatedPointer]]:
    """
    Inspects a function and returns how calling it mutates the args/result and
    creates view relationships between them.
    """

    # TODO: We should probably not use use setitem, but instead get particular
    # __setitem__ for class so we can differentiate based on type more easily?
    if function == operator.setitem:
        # setitem(dict, key, value)
        yield MutatedPointer(PositionalArg(0))
        if not is_immutable(args[2]):
            yield ViewOfPointers(PositionalArg(2), PositionalArg(0))
        return
    if function == operator.delitem:
        # delitem(dict, key)
        yield MutatedPointer(PositionalArg(0))
        return
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
            yield MutatedPointer(BoundSelfOfFunction())
            yield ViewOfPointers(BoundSelfOfFunction(), Result())
            return
    # Note: Future functions might require normalizing the args/kwargs with
    # inspect.signature.bind(args, kwargs) first
    return []


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
