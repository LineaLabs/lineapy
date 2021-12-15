from __future__ import annotations

import functools
import glob
import logging
import operator
import sys
import types
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import yaml
from pydantic import ValidationError

from lineapy.instrumentation.annotation_spec import (
    Criteria,
    ImplicitDependencyValue,
    InspectFunctionSideEffects,
    ModuleAnnotation,
    ViewOfValues,
    db,
    file_system,
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
    if criteria.function_name and criteria.function_name != function.__name__:
        return False
    if (
        criteria.class_instance
        and criteria.class_instance not in function.__module__
    ):
        return False
    if (
        criteria.class_method_name
        and criteria.class_method_name != function.__name__
    ):
        return False
    if (
        criteria.class_method_names
        and function.__name__ not in criteria.class_method_names
    ):
        return False
    if criteria.key_word_argument:
        if (
            kwargs.get(criteria.key_word_argument.arg_name, None)
            != criteria.key_word_argument.arg_value
        ):
            return False
    return True


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
    specs = get_specs()
    # TODO: create some hashing to avoid multiple loops
    for spec in specs:
        if spec.module in function.__module__:
            for annotation in spec.annotations:
                if check_function_against_annotation(
                    function, args, kwargs, annotation.criteria
                ):
                    for side_effect in annotation.side_effects:
                        yield side_effect
