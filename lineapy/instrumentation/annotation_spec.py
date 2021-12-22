from typing import Iterable, List, Optional, Union

from pydantic import BaseModel

"""

NOTE:
- For all mutation, we'll check if they are mutable. If this is a perf issue, we can re-evaluate...


TODO:
- also we should add annotation for base class, e.g., `sklearn.base`

- figure out how to capture the name of the DB
  - where the relevant SQL string is
  - where the relevant file name is

- Also the all caps strings are kinda hacky... 
  open to ideas for something better.
"""


class PositionalArg(BaseModel):
    positional_argument_index: int


class AllPositionalArgs(BaseModel):
    # ALL_POSITIONAL_ARGUMENTS
    all_positional_arguments: str


class KeywordArgument(BaseModel):
    argument_keyword: str


class BoundSelfOfFunction(BaseModel):
    """
    If the function is a bound method, this refers to the instance that was
    bound of the method.

    We are expecting "SELF_REF" though it's not needed
    """

    self_ref: str


class Result(BaseModel):
    """
    The result of a function call, used to describe a View.
    #  "RESULT"
    """

    result: str


class ExternalState(BaseModel):
    """
    Represents some reference to some state outside of the Python program.

    If we ever make a reference to an external state instance, we assume
    that it depends on any mutations of previous references.

    Elsewhere we need ExternalState to be hashable, it was pretty easy with Dataclass (frozen option), but with Pydantic, we have to add an extract hash function
    https://github.com/samuelcolvin/pydantic/issues/1303
    """

    external_state: str

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
    """

    # They are unique, like a set, but ordered for deterministic behavior
    views: list[ValuePointer]

    # def __init__(self, *xs: ValuePointer) -> None:
    #     self.views = list(xs)


class MutatedValue(BaseModel):
    """
    A value that is mutated when the function is called
    We are naming the fields with a repetition to the class name because we
      want Pydantic to be able to differentiate between the classes (without
      explicit class definitions.)
    """

    mutated_value: ValuePointer


class ImplicitDependencyValue(BaseModel):
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

    the names v. name is just a convenience for being able to have either a single item or a list of items.
    """

    function_names: List[str]


class FunctionName(BaseModel):
    function_name: str


class ClassMethodName(BaseModel):
    class_instance: str
    class_method_name: str


class ClassMethodNames(BaseModel):
    class_instance: str
    class_method_names: List[str]


class BaseClassMethodName(BaseModel):
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


# the FILE_SYSTEM and DB needs to match the yaml config
file_system = ExternalState(external_state="FILE_SYSTEM")
db = ExternalState(external_state="db")
