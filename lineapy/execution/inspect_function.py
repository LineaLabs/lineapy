from __future__ import annotations

import functools
import glob
import logging
import sys
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
from lineapy.utils import listify

logger = logging.getLogger(__name__)


def is_mutable(obj: object) -> bool:
    """
    Returns true if the object is mutable.
    """

    # Assume all hashable objects are immutable
    # I think this is incorrect...
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


# @functools.lru_cache()
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
    module: Optional[str] = None,
    base_module: Optional[str] = None,
):
    """
    Helper function for inspect_function.
    The checking for __self__ is for sometimes when it's a class instantiation method.
    """

    def check_class(criteria: Union[ClassMethodName, ClassMethodNames]):
        return (
            hasattr(function, "__self__")
            and module is not None
            and module in sys.modules
            and isinstance(
                function.__self__,  # type: ignore
                getattr(sys.modules[module], criteria.class_instance),
            )
        )

    if isinstance(criteria, FunctionName):
        if criteria.function_name == function.__name__:
            return True
        return False
    if isinstance(criteria, FunctionNames):
        if function.__name__ in criteria.function_names:
            return True
        return False
    if isinstance(criteria, ClassMethodName):
        if function.__name__ == criteria.class_method_name and check_class(
            criteria
        ):
            return True
        return False
    if isinstance(criteria, ClassMethodNames):
        if function.__name__ in criteria.class_method_names and check_class(
            criteria
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
            and function.__name__ == criteria.class_method_name
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

    def check_view_of_values(side_effect: ViewOfValues) -> ViewOfValues:
        for i, v in enumerate(side_effect.views):
            if isinstance(v, AllPositionalArgs):
                side_effect.views.pop(i)
                side_effect.views.extend(
                    (
                        PositionalArg(positional_argument_index=i)
                        for i, a in enumerate(args)
                    )
                )
                return side_effect
        return side_effect

    if isinstance(side_effect, ViewOfValues):
        # TODO: also need to check for mutability
        side_effect = check_view_of_values(side_effect)
        side_effect.views = list(
            filter(lambda x: is_reference_mutable(x), side_effect.views)
        )
        return side_effect
    if isinstance(side_effect, MutatedValue) and is_reference_mutable(
        side_effect.mutated_value
    ):
        return side_effect  # FIXME: this seemes odd...
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

    def _check_annotation(
        annotations: List[Annotation],
        module: Optional[str] = None,
        base_spec_module: Optional[str] = None,
    ):
        nonlocal has_yielded
        for annotation in annotations:
            if check_function_against_annotation(
                function,
                args,
                kwargs,
                annotation.criteria,
                module,
                base_spec_module,
            ):
                for side_effect in annotation.side_effects:
                    processed = process_side_effect(
                        side_effect, args, kwargs, result
                    )
                    if processed is not None:
                        yield processed
                        has_yielded = True
                if has_yielded:
                    return
        return

    # we have a special case here whose structure is not
    #   shared with any other cases...
    if (
        isinstance(function, BuiltinMethodType)
        and function.__name__ == "append"
        and isinstance(function.__self__, list)
    ):
        # list.append(value)
        yield MutatedValue(
            mutated_value=BoundSelfOfFunction(self_ref="SELF_REF")
        )
        if is_mutable(args[0]):
            yield ViewOfValues(
                views=[
                    BoundSelfOfFunction(self_ref="SELF_REF"),
                    PositionalArg(positional_argument_index=0),
                ]
            )
    else:
        specs, base_specs = get_specs()

        def get_root_module(fun: Callable):
            if hasattr(fun, "__module__") and fun.__module__ is not None:
                return fun.__module__.split(".")[0]
            return None

        if function.__module__ in specs:
            yield from _check_annotation(
                specs[function.__module__], module=function.__module__
            )
        root_module = get_root_module(function)
        if root_module is not None and root_module in specs:
            yield from _check_annotation(
                specs[root_module], module=root_module
            )
        if has_yielded:
            return

        if not isinstance(function, MethodType):
            # base classes have to be a method type, helps skip through
            #   some options
            return
        for base_spec_module in base_specs:
            # there doesn't seem to be a way to hash thru this...
            # so we'll loop for now
            yield from _check_annotation(
                base_specs[base_spec_module], base_spec_module=base_spec_module
            )
        return
