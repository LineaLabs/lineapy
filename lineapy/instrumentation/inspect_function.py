# from inspect import BoundArguments, signature
import operator
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

    This dataclass is used as the return value for inspecting a function, to
    provide more explicit names and types for the results.
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
    # TODO: add special casing for different functions
    # And then eventually probably try to specify most of it declaratively
    # Or infer from docstrings/names, definitions, etc.
    return InspectFunctionResult()

    # # Create a thunk for computing the bound arguments, since we can't get
    # # the signature of all functions (some function defined in C don't provide
    # # a signature).
    # def bound(function=function, args=args, kwargs=kwargs) -> BoundArguments:
    #     """
    #     Returns the bound arguments for the function, to normalize args/kwargs
    #     processing.
    #     """
    #     return signature(function).bind(*args, **kwargs)
