from __future__ import annotations

import glob
import logging
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from io import IOBase
from types import ModuleType
from typing import Callable, Dict, Hashable, Iterable, List, Optional, Tuple

import yaml
from pydantic import ValidationError

from lineapy.instrumentation.annotation_spec import (
    AllPositionalArgs,
    Annotation,
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

    Note that currently, `tempfile.NamedTemporaryFile()` is not mutable, and
    the semantics is actually correct, because it doesn't end up changing the
    file system. However, the following registers as normal files (which
    are mutable).

    ```python
    filename = NamedTemporaryFile().name
    handle = open(filename, "wb")
    ```
    """

    # We have to special case any types which are hashable, but are mutable.
    # Since there is no way to see if a class is mutable a priori, we could add a list of types
    # like this to our annotations
    mutable_hashable_types: Tuple[type, ...] = (
        ModuleType,
        type,
        type(iter([])),
        IOBase,
    )
    if "sklearn.base" in sys.modules:
        mutable_hashable_types += (sys.modules["sklearn.base"].BaseEstimator,)  # type: ignore

    # Special case some mutable hashable types
    if isinstance(obj, mutable_hashable_types):
        return True

    # Otherwise assume all hashable objects are immutable
    try:
        hash(obj)
    except Exception:
        return True
    return False


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
        logger.warning(
            f"Validation failed parsing {item} as annotation spec: {e}"
        )
        return None


def get_specs() -> Dict[str, List[Annotation]]:
    """
    yaml specs are for non-built in functions.
    Captures all the .annotations.yaml files in the lineapy directory.
    """
    relative_path = "../*.annotations.yaml"
    path = os.path.join(os.path.dirname(__file__), relative_path)
    valid_specs: Dict[str, List[Annotation]] = defaultdict(list)
    for filename in glob.glob(path):
        with open(filename, "r") as f:
            doc = yaml.safe_load(f)
            for item in doc:
                v = validate(item)
                if v is None:
                    continue
                valid_specs[v.module].extend(v.annotations)
    return valid_specs


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


@dataclass
class FunctionInspectorParsed:
    """
    Contains the parsed function inspector criteria.
    """

    # Function criteria
    function_to_side_effects: Dict[
        Callable, List[InspectFunctionSideEffect]
    ] = field(default_factory=lambda: defaultdict(list))
    # Method criteria
    method_name_to_type_to_side_effects: Dict[
        str, Dict[type, List[InspectFunctionSideEffect]]
    ] = field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))
    # Method keyword argument criteria
    keyword_name_and_value_to_type_to_side_effects: Dict[
        Tuple[str, Hashable], Dict[type, List[InspectFunctionSideEffect]]
    ] = field(default_factory=lambda: defaultdict(lambda: defaultdict(list)))

    def inspect(
        self, fn: Callable, kwargs: Dict[str, object]
    ) -> Optional[List[InspectFunctionSideEffect]]:
        """
        Inspect a function call and return a list of side effects, if it matches any of the annotations
        """
        # We assume a function is a method if it has a __self__ and the __self__  is not a Module
        # Note that for functions defines in C, like `setitem`, they have a __self__, but it's the
        # module they were defined in, in `setitems` case, `operator`, so that's why we need the isinstance
        # check
        obj = getattr(fn, "__self__", None)
        is_method = obj is not None and not isinstance(obj, ModuleType)

        # If it's a function, we just do a simple lookup to see if it's exactly equal to any functions we saved
        if not is_method:
            return self.function_to_side_effects.get(fn, None)
        # If it's a class instance however, we have to consider superclasses, so we first do a lookup
        # on the name, then check for isinstance
        method_name = fn.__name__
        for tp, side_effects in self.method_name_to_type_to_side_effects[
            method_name
        ].items():
            if isinstance(obj, tp):
                return side_effects
        # Finally, if we haven't found something yet, try the keyword names mapping on the method
        for k, v in kwargs.items():
            # Ignore any non hasable keyword args we pass in
            if not isinstance(v, Hashable):
                continue  # type: ignore
            for (
                tp,
                side_effects,
            ) in self.keyword_name_and_value_to_type_to_side_effects[
                (k, v)
            ].items():
                if isinstance(obj, tp):
                    return side_effects
        return None

    def add_annotations(
        self, module: ModuleType, annotations: List[Annotation]
    ) -> None:
        """
        Parse a list of annotations and look them up to add them to our parsed criteria.
        """
        for annotation in annotations:
            self._add_annotation(
                module, annotation.criteria, annotation.side_effects
            )

    def _add_annotation(
        self,
        module: ModuleType,
        criteria: Criteria,
        side_effects: List[InspectFunctionSideEffect],
    ) -> None:
        if isinstance(criteria, KeywordArgumentCriteria):
            class_ = getattr(module, criteria.class_instance)
            self.keyword_name_and_value_to_type_to_side_effects[
                (criteria.keyword_arg_name, criteria.keyword_arg_value)
            ][class_] = side_effects
        elif isinstance(criteria, FunctionNames):
            for name in criteria.function_names:
                fn = getattr(module, name)
                self.function_to_side_effects[fn] = side_effects
        elif isinstance(criteria, FunctionName):
            fn = getattr(module, criteria.function_name)
            self.function_to_side_effects[fn] = side_effects
        elif isinstance(criteria, ClassMethodName):
            tp = getattr(module, criteria.class_instance)
            self.method_name_to_type_to_side_effects[
                criteria.class_method_name
            ][tp] = side_effects
        elif isinstance(criteria, ClassMethodNames):
            tp = getattr(module, criteria.class_instance)
            for name in criteria.class_method_names:
                self.method_name_to_type_to_side_effects[name][
                    tp
                ] = side_effects
        else:
            raise NotImplementedError(criteria)


@dataclass
class FunctionInspector:
    """
    The FunctionInspector does two different loading steps.

    1. Load all the specs from disk with `get_specs`. This happens once on creation of the object.
    2. On initialization, and before every spec call, go through all the specs and "parse" any for modules we have already imported,
       which means turning the criteria into in memory objects, we can compare against when inspecting.
    """

    # Dictionary contains all the specs we haven't parsed yet, because they correspond to un-imported modules
    specs: Dict[str, List[Annotation]] = field(default_factory=get_specs)
    # Annotations we have already parsed, since we have already imported these modules.
    parsed: FunctionInspectorParsed = field(
        default_factory=FunctionInspectorParsed
    )

    def _parse(self) -> None:
        """
        Parses all specs which are for modules we have imported
        """
        for module_name in list(self.specs.keys()):
            module = get_imported_module(module_name)
            if not module:
                continue
            self.parsed.add_annotations(
                module,
                # Pop the spec once we have processed it
                self.specs.pop(module_name),
            )

    def __post_init__(self):
        self._parse()

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
        # Try re-parsing during each function call, incase other modules were imported we can analyse
        self._parse()
        side_effects = self.parsed.inspect(function, kwargs) or []
        for side_effect in side_effects:
            processed_side_effect = process_side_effect(
                side_effect, args, kwargs, result
            )
            if processed_side_effect:
                yield processed_side_effect


def get_imported_module(name: str) -> Optional[ModuleType]:
    """
    Return a module, if it has been imported.

    Also handles the corner case where a submodule has not been imported, but is accessible
    as an attribute on the parent module. This is needed for the example `tensorflow.keras.utils`, which
    is not imported when importing `tensorflow`, but is accessible as a property of `tensorflow`.
    """
    if name in sys.modules:
        return sys.modules[name]
    *parent_names, submodule_name = name.split(".")
    if not parent_names:
        return None
    parent_module = get_imported_module(".".join(parent_names))
    if not parent_module:
        return None
    return getattr(parent_module, submodule_name, None)
