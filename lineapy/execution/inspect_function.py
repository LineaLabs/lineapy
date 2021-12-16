from __future__ import annotations

import functools
import glob
import logging
import sys
from types import BuiltinMethodType
from typing import Any, Callable, Dict, List, Optional

import yaml
from pydantic import ValidationError

from lineapy.instrumentation.annotation_spec import (
    BoundSelfOfFunction,
    ClassMethodName,
    ClassMethodNames,
    Criteria,
    FunctionName,
    InspectFunctionSideEffect,
    InspectFunctionSideEffects,
    KeywordArgumentCriteria,
    ModuleAnnotation,
    MutatedValue,
    PositionalArg,
    Result,
    ValuePointer,
    ViewOfValues,
    all_positional_args_instance,
)

logger = logging.getLogger(__name__)


def is_mutable(obj: object) -> bool:
    """
    Returns true if the object is mutable.
    """

    # Assume all hashable objects are immutable
    try:
        hash(obj)
    except Exception:
        return True
    return False


def try_import(name: str) -> Any:
    """
    Returns the modules, if it has been imported already.
    """
    return sys.modules.get(name, None)


def validate(item: Dict) -> Optional[ModuleAnnotation]:
    try:
        spec = ModuleAnnotation(**item)
        # check if the module is relevant for this run
        if try_import(spec.module) is None:
            return None
        return spec
    except ValidationError as e:
        # want to warn the user but not break the whole thing
        logger.warning(f"Validation failed for annotation spec: {e}")
        return None


@functools.lru_cache()
def get_specs() -> List[ModuleAnnotation]:
    """
    yaml specs are for non-built in functions.
    will capture all the .annotations.yaml files in the `instrumentation` directory.
    """
    # apparently the path is on the top level
    path = "./lineapy/instrumentation/*.annotations.yaml"
    all_valid_specs = []
    for filename in glob.glob(path):
        with open(filename, "r") as f:
            doc = yaml.safe_load(f)
            all_valid_specs += list(
                filter(None, [validate(item) for item in doc])
            )
    return all_valid_specs


def check_function_against_annotation(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    criteria: Criteria,
):
    """
    Helper function for inspect_function.
    """
    if (
        isinstance(criteria, FunctionName)
        and criteria.function_name != function.__name__
    ):
        return False
    if (
        isinstance(criteria, ClassMethodName)
        and criteria.class_instance not in function.__module__
        and function.__name__ != criteria.class_method_name
    ):
        return False
    if (
        isinstance(criteria, ClassMethodNames)
        and criteria.class_instance not in function.__module__
        and function.__name__ not in criteria.class_method_names
    ):
        return False
    if isinstance(criteria, KeywordArgumentCriteria) and (
        kwargs.get(criteria.keyword_arg_name, None)
        != criteria.keyword_arg_value
    ):
        return False
    return True


def process_side_effect(
    side_effect: InspectFunctionSideEffect, args: list, result: object
) -> Optional[InspectFunctionSideEffect]:
    def is_reference_mutable(p: ValuePointer) -> bool:
        if isinstance(p, Result):
            return is_mutable(result)
        if isinstance(p, PositionalArg):
            return is_mutable(args[p.positional_argument_index])
        # shouldn't really be called
        # TODO: maybe bring back our custom errors?
        raise Exception("The other cases should not have been called.")

    if isinstance(side_effect, ViewOfValues):
        # TODO: also need to check for mutability
        i = side_effect.views.index(all_positional_args_instance)  # type: ignore
        if i != -1:
            side_effect.views.pop(i)
            side_effect.views.extend(
                (PositionalArg(i) for i, a in enumerate(args))
            )

        side_effect.views = list(
            filter(lambda x: is_mutable(x), side_effect.views)
        )
    if isinstance(side_effect, MutatedValue) and is_reference_mutable(
        side_effect.mutated_value
    ):
        return side_effect
    return side_effect
    # check if they are mutable


def inspect_function(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    result: object,
) -> InspectFunctionSideEffects:
    """
    Inspects a function and returns how calling it mutates the args/result and
    creates view relationships between them.
    """
    # we have a special case here whose structure is not
    #   shared with any other cases...
    if (
        isinstance(function, BuiltinMethodType)
        and function.__name__ == "append"
        and isinstance(function.__self__, list)
    ):
        # list.append(value)
        yield MutatedValue(BoundSelfOfFunction())
        if is_mutable(args[0]):
            yield ViewOfValues(BoundSelfOfFunction(), PositionalArg(0))
    else:
        specs = get_specs()
        # TODO: create some hashing to avoid multiple loops
        for spec in specs:
            if spec.module in function.__module__:
                for annotation in spec.annotations:
                    if check_function_against_annotation(
                        function, args, kwargs, annotation.criteria
                    ):
                        for side_effect in annotation.side_effects:
                            processed = process_side_effect(
                                side_effect, args, result
                            )
                            if processed is not None:
                                yield processed
