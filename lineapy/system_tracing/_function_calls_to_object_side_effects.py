from typing import Iterable

from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.annotation_spec import InspectFunctionSideEffect
from lineapy.system_tracing._object_side_effect import ObjectSideEffect
from lineapy.system_tracing.function_call import FunctionCall


def function_calls_to_object_side_effects(
    function_inspector: FunctionInspector,
    function_calls: Iterable[FunctionCall],
) -> Iterable[ObjectSideEffect]:
    for fc in function_calls:
        for side_effect in function_inspector.inspect(
            fc.fn, fc.args, fc.kwargs, fc.res
        ):
            yield to_object_side_effect(side_effect, fc)


# TODO: Make singledispatch
def to_object_side_effect(
    side_effect: InspectFunctionSideEffect, function_call: FunctionCall
) -> ObjectSideEffect:
    raise NotImplementedError()
