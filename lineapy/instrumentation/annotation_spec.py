from typing import List, Optional, Union

from pydantic import BaseModel

"""
NOTE:
- All the classes in the `ValuePointer` follow this weird structure where
  their field entries duplicate the class name---this is so that when we load
  the YAMLs, they can differentiate the class based just by the field names.
  - Also the string values for `AllPositionalArgs`, `BoundSelfOfFunction`, 
    and `Result` are useless as well---just there so that we abide by the
    yaml structure. It's not very elegant and we can refactor this later.

TODO:
- figure out how to capture the name of the DB
  - where the relevant SQL string is
  - where the relevant file name is
"""


class PositionalArg(BaseModel):
    """
    References a positional argument. E.g., in `foo(a, b)`, `a` would have a
    positional argument of 0.
    """

    positional_argument_index: int


class KeywordArgument(BaseModel):
    """
    References a keyword argument. E.g., in `foo(a=1, b=2)`, `a` would have a
    keyword argument of `a`.
    """

    argument_keyword: str


class AllPositionalArgs(BaseModel):
    """
    References all positional arguments. E.g., in `foo(a, b)`, `a` and `b`.

    Expecting the string to be set the value "ALL_POSITIONAL_ARGUMENTS"
    """

    all_positional_arguments: str


class BoundSelfOfFunction(BaseModel):
    """

    References the bound self of a function. E.g., in `foo.test(a, b)`,
    `foo` would be the bound self.

    If the function is a bound method, this refers to the instance that was
    bound of the method.

    We are expecting "SELF_REF" though it's not needed. I was not able to
    set it as "default" due to some YAML snafus.
    """

    self_ref: str


class Result(BaseModel):
    """
    References the result of a function. E.g., in `bar = foo(a, b)`, `bar` would
    The result of a function call.


    We are expecting "RESULT" though it's not needed.
    """

    result: str


class ExternalState(BaseModel):
    """
    Represents some reference to some state outside of the Python program.

    If we ever make a reference to an external state instance, we assume
    that it depends on any mutations of previous references.

    Elsewhere we need ExternalState to be hashable, it was pretty easy with
    Dataclass (frozen option), but with Pydantic, we have to add an extra
    hash function
    https://github.com/samuelcolvin/pydantic/issues/1303
    """

    external_state: str

    @property
    def __name__(self):
        return self.external_state

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


# A value representing a pointer to some value related to a function call
ValuePointer = Union[
    PositionalArg,
    KeywordArgument,
    Result,
    BoundSelfOfFunction,
    ExternalState,
    AllPositionalArgs,
]


class ViewOfValues(BaseModel):
    """
    A set of values which all potentially refer to shared pointers
    So that if one is mutated, the rest might be as well.
    They are unique, like a set, but ordered for deterministic behavior,
    hence a list.
    """

    views: List[ValuePointer]


class MutatedValue(BaseModel):
    """
    A value that is mutated when the function is called.
    We are naming the fields with a repetition to the class name because we
      want Pydantic to be able to differentiate between the classes (without
      explicit class definitions.)
    """

    mutated_value: ValuePointer


class ImplicitDependencyValue(BaseModel):
    """
    References state that is implicitly depended on by the function.
    Currently it's used for external state like db + filesystem.
    """

    dependency: ValuePointer


InspectFunctionSideEffect = Union[
    ViewOfValues, MutatedValue, ImplicitDependencyValue
]


class KeywordArgumentCriteria(BaseModel):
    """
    Currently only used for the pandas inplace argument.
    We might need to augment how we parse it in the future for other inputs.
    """

    keyword_arg_name: str
    keyword_arg_value: int


class FunctionNames(BaseModel):
    """
    References a list of function names.
    """

    function_names: List[str]


class FunctionName(BaseModel):
    """
    A convenience for a list of items.
    """

    function_name: str


class ClassMethodName(BaseModel):
    """
    An example is `df.to_sql`, the `class_instance` is then the string "DataFrame",
    and the `class_method_name` is the string "to_sql".
    """

    class_instance: str
    class_method_name: str


class ClassMethodNames(BaseModel):
    """
    A shorthand for a list of class method names. Useful for cases like
    df.to_sql, df.to_csv, etc.
    """

    class_instance: str
    class_method_names: List[str]


class BaseClassMethodName(BaseModel):
    """
    Baseclass methods allow us to cover more cases.

    For instance, in sklearn, many `fit` methods are on different types of
      estimators that are subclasses of `BaseEstimator`.

    So the `class_instance` is the string "BaseEstimator",
      and the `class_method_name` is the string "fit".
    """

    base_class: str
    class_method_name: str


# Criteria for a single annotation
Criteria = Union[
    KeywordArgumentCriteria,
    FunctionNames,
    ClassMethodNames,
    FunctionName,
    ClassMethodName,
    BaseClassMethodName,
]


class Annotation(BaseModel):
    criteria: Criteria
    side_effects: List[InspectFunctionSideEffect]


class ModuleAnnotation(BaseModel):
    module: Optional[str]
    base_module: Optional[str]
    annotations: List[Annotation]

    class Config:
        allow_mutation = False
        extra = "forbid"
