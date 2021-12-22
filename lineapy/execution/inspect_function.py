from __future__ import annotations

import functools
import glob
import logging
import sys
from types import BuiltinMethodType, MethodType
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import yaml
from pydantic import ValidationError

from lineapy.instrumentation.annotation_spec import (
    AllPositionalArgs,
    Annotation,
    BaseClassMethodName,
    BoundSelfOfFunction,
    ClassMethodName,
    ClassMethodNames,
    Criteria,
    FunctionName,
    InspectFunctionSideEffect,
    KeywordArgumentCriteria,
    ModuleAnnotation,
    MutatedValue,
    PositionalArg,
    Result,
    ValuePointer,
    ViewOfValues,
)
from lineapy.utils import listify

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
        if spec.module is not None and try_import(spec.module) is None:
            return None
        if (
            spec.base_module is not None
            and try_import(spec.base_module) is None
        ):
            return None
        return spec
    except ValidationError as e:
        # want to warn the user but not break the whole thing
        logger.warning(f"Validation failed for annotation spec: {e}")
        return None


@functools.lru_cache()
def get_specs() -> Tuple[
    Dict[str, List[Annotation]], Dict[str, List[Annotation]]
]:
    """
    yaml specs are for non-built in functions.
    will capture all the .annotations.yaml files in the `instrumentation` directory.
    """
    # apparently the path is on the top level
    path = "./lineapy/instrumentation/*.annotations.yaml"
    valid_specs = {}
    valid_base_specs = {}
    for filename in glob.glob(path):
        with open(filename, "r") as f:
            doc = yaml.safe_load(f)
            for item in doc:
                v = validate(item)
                if v is not None:
                    if v.module is not None:
                        valid_specs[v.module] = v.annotations
                    else:
                        valid_base_specs[v.base_module] = v.annotations
    return valid_specs, valid_base_specs


def check_function_against_annotation(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    criteria: Criteria,
    base_module: Optional[str] = None,
):
    """
    Helper function for inspect_function.
    """
    if isinstance(criteria, FunctionName):
        if criteria.function_name == function.__name__:
            return True
        return False
    if isinstance(criteria, ClassMethodName):
        if (
            criteria.class_instance == function.__self.__.__module__
            and function.__name__ == criteria.class_method_name
        ):
            return True
        return False
    if isinstance(criteria, ClassMethodNames):
        if (
            criteria.class_instance == function.__self.__.__module__
            and function.__name__ in criteria.class_method_names
        ):
            return True
        return False
    if isinstance(criteria, KeywordArgumentCriteria):
        if (
            kwargs.get(criteria.keyword_arg_name, None)
            == criteria.keyword_arg_value
        ):
            return True
        return False
    if isinstance(criteria, BaseClassMethodName):
        if (
            base_module is not None
            and function.__name__ == criteria.class_method_name
            and (
                isinstance(
                    function.__self___,
                    getattr(try_import(base_module), criteria.base_class),
                )
            )
        ):
            return True
        return False

    raise ValueError(f"Unknown criteria: {criteria} of type {type(criteria)}")


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

    def check_view_of_values(side_effect: ViewOfValues):
        for i, v in enumerate(side_effect.views):
            if isinstance(v, AllPositionalArgs):
                side_effect.views.pop(i)
                side_effect.views.extend(
                    (
                        PositionalArg(positional_argument_index=i)
                        for i, a in enumerate(args)
                    )
                )
            return

    if isinstance(side_effect, ViewOfValues):
        # TODO: also need to check for mutability
        check_view_of_values(side_effect)
        side_effect.views = list(
            filter(lambda x: is_mutable(x), side_effect.views)
        )
    if isinstance(side_effect, MutatedValue) and is_reference_mutable(
        side_effect.mutated_value
    ):
        return side_effect
    return side_effect
    # check if they are mutable


@listify
def inspect_function(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    result: object,
) -> Iterable[InspectFunctionSideEffect]:
    """
    Inspects a function and returns how calling it mutates the args/result and
    creates view relationships between them.
    """
    has_yielded = False

    def _check_annotation(annotations: List[Annotation]):
        nonlocal has_yielded
        for annotation in annotations:
            if check_function_against_annotation(
                function, args, kwargs, annotation.criteria
            ):
                for side_effect in annotation.side_effects:
                    processed = process_side_effect(side_effect, args, result)
                    if processed is not None:
                        yield processed
                        has_yielded = True
                if has_yielded:
                    return

    # we have a special case here whose structure is not
    #   shared with any other cases...
    if (
        isinstance(function, BuiltinMethodType)
        and function.__name__ == "append"
        and isinstance(function.__self__, list)
    ):
        # list.append(value)
        yield MutatedValue(mutated_value=BoundSelfOfFunction())
        if is_mutable(args[0]):
            yield ViewOfValues(
                views=[
                    BoundSelfOfFunction(),
                    PositionalArg(positional_argument_index=0),
                ]
            )
    else:
        specs, base_specs = get_specs()
        if function.__module__ in specs:
            yield from _check_annotation(specs[function.__module__])
        if has_yielded:
            return

        # there doesn't seem to be a way to hash thru this...
        # so we'll loop for now,
        for base_spec_module in base_specs:
            yield from _check_annotation(base_specs[base_spec_module])
        return
