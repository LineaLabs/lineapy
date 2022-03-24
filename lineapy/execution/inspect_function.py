from __future__ import annotations

import glob
import logging
import os
import sys
from dataclasses import dataclass, field
from types import BuiltinMethodType, MethodType
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

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
    ExternalState,
    FunctionName,
    FunctionNames,
    InspectFunctionSideEffect,
    KeywordArgument,
    KeywordArgumentCriteria,
    ModuleAnnotation,
    MutatedValue,
    PositionalArg,
    Result,
    ValuePointer,
    ViewOfValues,
)

logger = logging.getLogger(__name__)

"""
helper functions
"""


def is_mutable(obj: object) -> bool:
    """
    Returns true if the object is mutable.
    """

    # Assume all hashable objects are immutable
    # I (yifan) think this is incorrect, but keeping the dead code
    #   here in case we run into some issues again

    # try:
    #     hash(obj)
    # except Exception:
    #     return True
    # return False
    if isinstance(obj, (str, int, bool, float, tuple, frozenset)):
        return False
    else:
        return True


def try_import(name: str) -> Any:
    """
    Returns the modules, if it has been imported already.
    """
    return sys.modules.get(name, None)


def validate(item: Dict) -> Optional[ModuleAnnotation]:
    """
    We cannot filer the specs by module, because it might be loaded later.
    This causes a bit of inefficiency in our function inspection, but we
    can fix later if it's a problem.
    """
    try:
        spec = ModuleAnnotation(**item)
        return spec
    except ValidationError as e:
        # want to warn the user but not break the whole thing
        logger.warning(f"Validation failed for annotation spec: {e}")
        return None


def get_specs() -> Dict[str, List[Annotation]]:
    """
    yaml specs are for non-built in functions.
    Captures all the .annotations.yaml files in the lineapy directory.
    """
    relative_path = "../*.annotations.yaml"
    path = os.path.join(os.path.dirname(__file__), relative_path)
    valid_specs: Dict[str, List[Annotation]] = {}
    for filename in glob.glob(path):
        with open(filename, "r") as f:
            doc = yaml.safe_load(f)
            for item in doc:
                v = validate(item)
                if v is None:
                    continue
                valid_specs[v.module] = v.annotations
    return valid_specs


def _check_class(
    criteria: Union[ClassMethodName, ClassMethodNames],
    module: Optional[str],
    function: Callable,
):
    """
    helper
    """
    return (
        hasattr(function, "__self__")
        and module is not None
        and module in sys.modules
        and isinstance(
            function.__self__,  # type: ignore
            getattr(sys.modules[module], criteria.class_instance),
        )
    )


def check_function_against_annotation(
    function: Callable,
    # args: list[object], # we'll prob need this later...
    kwargs: dict[str, object],
    criteria: Criteria,
    module: str,
):
    """
    Helper function for inspect_function.
    The checking for __self__ is for sometimes when it's a class instantiation method.
    """
    # torch nn Predictor has no __name__
    function_name = getattr(function, "__name__", None)
    if isinstance(criteria, FunctionName):
        if criteria.function_name == function_name:
            return True
        return False
    if isinstance(criteria, FunctionNames):
        if function_name in criteria.function_names:
            return True
        return False
    if isinstance(criteria, ClassMethodName):
        if function_name == criteria.class_method_name and _check_class(
            criteria, module, function
        ):
            return True
        return False
    if isinstance(criteria, ClassMethodNames):
        if function_name in criteria.class_method_names and _check_class(
            criteria, module, function
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
    if isinstance(criteria, BaseClassMethodName) and hasattr(
        function, "__self__"
    ):
        if (
            base_module is not None
            and function_name == criteria.class_method_name
            and hasattr(try_import(base_module), criteria.base_class)
            and (
                isinstance(
                    function.__self__,  # type: ignore
                    getattr(try_import(base_module), criteria.base_class),
                )
            )
        ):
            return True
        return False

    raise ValueError(f"Unknown criteria: {criteria} of type {type(criteria)}")


def new_side_effect_without_all_positional_arg(
    side_effect: ViewOfValues,
    args: list,
) -> ViewOfValues:
    """
    This method must NOT modify the original side_effect, since these
    annotations are dependent on the runtime values that are different
    for each call---AllPositionalArgs will have a different set of arguments.

    Note that we might need to add something like "all keyword arguments", but
    that use case hasn't come up yet.
    """
    new_side_effect = ViewOfValues(views=[])
    for view in side_effect.views:
        new_side_effect.views.append(view.copy(deep=True))
    for i, v in enumerate(new_side_effect.views):
        if isinstance(v, AllPositionalArgs):
            new_side_effect.views.pop(i)
            new_side_effect.views.extend(
                (
                    PositionalArg(positional_argument_index=i)
                    for i, a in enumerate(args)
                )
            )
            return new_side_effect
    return new_side_effect


def process_side_effect(
    side_effect: InspectFunctionSideEffect,
    args: list,
    kwargs: dict[str, object],
    result: object,
) -> Optional[InspectFunctionSideEffect]:
    def is_reference_mutable(p: ValuePointer) -> bool:
        if isinstance(p, Result):
            return is_mutable(result)
        if isinstance(p, PositionalArg):
            return is_mutable(args[p.positional_argument_index])
        if isinstance(p, BoundSelfOfFunction) or isinstance(p, ExternalState):
            return True  # object
        if isinstance(p, KeywordArgument):
            return is_mutable(kwargs[p.argument_keyword])
        raise Exception(f"ValuePointer {p} of type {type(p)} not handled.")

    if isinstance(side_effect, ViewOfValues):
        new_side_effect = new_side_effect_without_all_positional_arg(
            side_effect, args
        )
        new_side_effect.views = list(
            filter(lambda x: is_reference_mutable(x), new_side_effect.views)
        )

        # If we don't have at least two items to view each other, skip this one
        if len(new_side_effect.views) < 2:
            return None
        return new_side_effect

    if isinstance(side_effect, MutatedValue):
        if is_reference_mutable(side_effect.mutated_value):
            return side_effect
        return None
    return side_effect


def _check_annotation(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    result: object,
    spec_annotations: List[Annotation],
    module: str,
):
    for annotation in spec_annotations:
        if check_function_against_annotation(
            function,
            # args, # prob will need soon
            kwargs,
            annotation.criteria,
            module,
        ):
            for side_effect in annotation.side_effects:
                processed = process_side_effect(
                    side_effect, args, kwargs, result
                )
                if processed is not None:
                    yield processed
    return


@dataclass
class FunctionInspector:
    specs: Dict[str, List[Annotation]] = field(default_factory=dict)

    def inspect(
        self,
        function: Callable,
        args: list[object],
        kwargs: dict[str, object],
        result: object,
    ) -> Iterable[InspectFunctionSideEffect]:
        """
        Inspects a function and returns how calling it mutates the args/result and
        creates view relationships between them.
        """

        yield from _check_annotation(
            function,
            args,
            kwargs,
            result,
            self.specs[module],
            module,
        )
