from typing import Iterable

from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.annotation_spec import (
    AllPositionalArgs,
    BoundSelfOfFunction,
    ExternalState,
    ImplicitDependencyValue,
    InspectFunctionSideEffect,
    KeywordArgument,
    MutatedValue,
    PositionalArg,
    Result,
    ValuePointer,
    ViewOfValues,
)
from lineapy.system_tracing._object_side_effect import (
    ImplicitDependencyObject,
    MutatedObject,
    ObjectSideEffect,
    ViewOfObjects,
)
from lineapy.system_tracing.function_call import FunctionCall
from lineapy.utils.lineabuiltins import LINEA_BUILTINS


def function_calls_to_object_side_effects(
    function_inspector: FunctionInspector,
    function_calls: Iterable[FunctionCall],
) -> Iterable[ObjectSideEffect]:
    """
    Turn the function calls into the side effects in terms of the Python objects.
    For example, "the object [1, 2, 3] was mutated."
    """
    for fc in function_calls:
        for side_effect in function_inspector.inspect(
            fc.fn, fc.args, fc.kwargs, fc.res
        ):
            yield from to_object_side_effects(side_effect, fc)


def to_object_side_effects(
    side_effect: InspectFunctionSideEffect, function_call: FunctionCall
) -> Iterable[ObjectSideEffect]:
    if isinstance(side_effect, ViewOfValues):
        yield ViewOfObjects(
            [
                o
                for p in side_effect.views
                for o in pointer_to_objects(p, function_call)
            ]
        )
    elif isinstance(side_effect, MutatedValue):
        for o in pointer_to_objects(side_effect.mutated_value, function_call):
            yield MutatedObject(o)
    elif isinstance(side_effect, ImplicitDependencyValue):
        for o in pointer_to_objects(side_effect.dependency, function_call):
            yield ImplicitDependencyObject(o)
    else:
        raise NotImplementedError()


def pointer_to_objects(
    pointer: ValuePointer, function_call: FunctionCall
) -> Iterable[object]:
    """
    Translate a pointer to the actual values, based on the values in the function call.
    """
    if isinstance(pointer, PositionalArg):
        yield function_call.args[pointer.positional_argument_index]
    elif isinstance(pointer, KeywordArgument):
        yield function_call.kwargs[pointer.argument_keyword]
    elif isinstance(pointer, AllPositionalArgs):
        yield from function_call.args
    elif isinstance(pointer, BoundSelfOfFunction):
        yield function_call.fn.__self__  # type: ignore
    elif isinstance(pointer, Result):
        yield function_call.res
    elif isinstance(pointer, ExternalState):
        yield LINEA_BUILTINS[pointer.external_state]
    else:
        raise NotImplementedError(str(type(pointer)))
