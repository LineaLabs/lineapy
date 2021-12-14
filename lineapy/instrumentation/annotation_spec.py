from typing import Iterable, List, Optional, Union

from pydantic import BaseModel

"""
TODO: figure out how to capture the name of the DB
  - where the relevant SQL string is
  - where the relevant file name is
"""


class PositionalArg(BaseModel):
    positional_argument_index: int


class KeywordArgument(BaseModel):
    argument_keyword: str


class BoundSelfOfFunction(BaseModel):
    """
    If the function is a bound method, this refers to the instance that was
    bound of the method.
    """

    self: str = "SELF"


class Result(BaseModel):
    """
    The result of a function call, used to describe a View.
    """

    result: str = "RESULT"


class ExternalState(BaseModel):
    """
    Represents some reference to some state outside of the Python program.

    If we ever make a reference to an external state instance, we assume
    that it depends on any mutations of previous references.
    """

    external_state: str


# A value representing a pointer to some value related to a function call
ValuePointer = Union[
    PositionalArg,
    KeywordArgument,
    Result,
    BoundSelfOfFunction,
    ExternalState,
]


class ViewOfValues(BaseModel):
    """
    A set of values which all potentially refer to shared pointers
    So that if one is mutated, the rest might be as well.
    """

    # They are unique, like a set, but ordered for deterministic behavior
    views: list[ValuePointer]

    def __init__(self, *xs: ValuePointer) -> None:
        self.views = list(xs)


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
InspectFunctionSideEffects = Iterable[InspectFunctionSideEffect]


class KeywordArgumentCriteria(BaseModel):
    """
    Currently only used for the pandas inplace argument.
    We might need to augment how we parse it in the future for other inputs.
    """

    arg_name: str
    arg_value: int


class Criteria(BaseModel):
    """
    Criteria for a single annotation

    the names v. name is just a convenience for being able to have either a single item or a list of items.

    Also, really should be a union type but I'm getting lazy here...
    """

    key_word_argument: Optional[KeywordArgumentCriteria] = None
    function_names: Optional[List[str]]
    function_name: Optional[str]
    class_instance: Optional[str]
    class_method_name: Optional[str]
    class_method_names: Optional[List[str]]


class Annotation(BaseModel):
    criteria: Criteria
    side_effects: InspectFunctionSideEffects


class ModuleAnnotation(BaseModel):
    module: str
    annotations: List[Annotation]


# the FILE_SYSTEM and DB needs to match the yaml config
file_system = ExternalState(external_state="FILE_SYSTEM") 
db = ExternalState(external_state="db")
