"""
.. note::

    You can find a higher level documentation about how library annotations in
    lineapy work, and how to contribute :ref:`here <lib_annotations>`.
"""

from typing import List, Union

import pydantic

"""
DEV NOTE:
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


class BaseModel(pydantic.BaseModel):
    """
    Forbid extras on baseclass so typos will raise an error
    """

    class Config:
        extra = "forbid"


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

    Expecting the string to be set the value "ALL_POSITIONAL_ARGUMENTS"---see :class:`~lineapy.instrumentation.annotation_spec.Result` for an explanation
    """

    all_positional_arguments: str


class BoundSelfOfFunction(BaseModel):
    """

    References the bound self of a function. E.g., in ``foo.test(a, b)``,
    `foo` would be the bound self.

    If the function is a bound method, this refers to the instance that was
    bound of the method.

    We are expecting "SELF_REF"---see :class:`~lineapy.instrumentation.annotation_spec.Result` for an explanation.
    """

    self_ref: str


class Result(BaseModel):
    """
    References the result of a function. E.g., in ``bar = foo(a, b)``, ``bar`` would
    The result of a function call.

    We are expecting "RESULT" for the field ``result``---though it's not needed
    for the python class, it is needed for yaml, and setting a default value
    makes the loader we use, pydantic, confused.
    """

    result: str


class ExternalState(BaseModel):
    """
    Represents some reference to some state outside of the Python program. The two types of external state supported are ``DB`` and ``file_system``.

    If we ever make a reference to an external state instance, we assume
    that it depends on any mutations of previous references.

    """

    external_state: str

    @property
    def __name__(self):
        return self.external_state

    def __hash__(self):
        """
        Elsewhere we need ``ExternalState`` to be hashable, it was pretty easy
        with Dataclass (frozen option), but with Pydantic, we have to add an
        extra hash function
        https://github.com/samuelcolvin/pydantic/issues/1303
        """
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

    Take the ``fit`` function in scikit-learn, if its assigned to a new variable,
    then the variable is aliased to the original variable.
    So we have the following annotation:

    .. code-block:: yaml

          - base_module: sklearn.base
            annotations:
            - criteria:
                base_class: BaseEstimator
                class_method_name: fit
                side_effects:
                - mutated_value:
                    self_ref: SELF_REF # self is a keyword...
                - views:
                - self_ref: SELF_REF
                - result: RESULT


    """

    views: List[ValuePointer]


class MutatedValue(BaseModel):
    """
    A value that is mutated when the function is called. Consider the example
    of the ``dump`` function in ``joblib``. It mutates the file_system, which
    is represented by :class:`~lineapy.lineapy.instrumentation.annotation_spec.ExternalState`.

    .. code-block:: yaml

        - module: joblib
          annotations:
          - criteria:
              function_name: dump
            side_effects:
            - mutated_value:
                external_state: file_system
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
    Currently only used for the pandas in-place argument.
    We might need to augment how we parse it in the future for other inputs.
    """

    keyword_arg_name: str
    keyword_arg_value: int
    class_instance: str


class FunctionNames(BaseModel):
    """
    References a list of function names (vs. a single one in :class:`~lineapy.instrumentation.annotation_spec.FunctionName`).

    One example is for the module `pandas` (and you can find the code `here <https://github.com/LineaLabs/lineapy/blob/main/lineapy/external.annotations.yaml>`__):

    .. code-block:: yaml

        - criteria:
            function_names:
            - upload_file
            - upload_fileobj

    """

    function_names: List[str]


class FunctionName(BaseModel):
    """
    A single function name (vs. a list in :class:`~lineapy.instrumentation.annotation_spec.FunctionNames`).
    """

    function_name: str


class ClassMethodName(BaseModel):
    """
    Specifies a **class** method name (as opposed to a function). An example is `df.to_sql`:

    .. code-block:: yaml

        - criteria:
            class_method_name: to_sql
            class_instance: DataFrame

    """

    class_instance: str
    class_method_name: str


class ClassMethodNames(BaseModel):
    """
    A shorthand for a list of class method names (vs. a single one
    as in :class:`~lineapy.instrumentation.annotation_spec.ClassMethodName`).

    .. code-block:: yaml

        - criteria:
            class_method_names:
            - to_csv
            - to_parquet
            class_instance: DataFrame

    """

    class_instance: str
    class_method_names: List[str]


# Criteria for a single annotation
Criteria = Union[
    KeywordArgumentCriteria,
    FunctionNames,
    ClassMethodNames,
    FunctionName,
    ClassMethodName,
]


class Annotation(BaseModel):
    """
    An annotation contains a single criteria for the function call,
    and the corresponding `side_effects` of the function call.

    There are currently six types of criteria, all of which are explained in their respective classes:

    * :class:`~lineapy.instrumentation.annotation_spec.KeywordArgumentCriteria`
    * :class:`~lineapy.instrumentation.annotation_spec.FunctionNames`
    * :class:`~lineapy.instrumentation.annotation_spec.ClassMethodNames`
    * :class:`~lineapy.instrumentation.annotation_spec.FunctionName`
    * :class:`~lineapy.instrumentation.annotation_spec.ClassMethodName`

    There are currently three types of side_effects:

    * :class:`~lineapy.instrumentation.annotation_spec.ViewOfValues`
    * :class:`~lineapy.instrumentation.annotation_spec.MutatedValue`
    * :class:`~lineapy.instrumentation.annotation_spec.ImplicitDependencyValue`
    """

    criteria: Criteria
    side_effects: List[InspectFunctionSideEffect]


class ModuleAnnotation(BaseModel):
    """
    An annotation yaml file is composed of a list of :class:`~lineapy.instrumentation.annotation_spec.ModuleAnnotations` (this class), which is to say that the annotations are hierarchically organized
    by what module the annotation is associated with, such as ``pandas`` and ``boto3``.
    """

    module: str
    annotations: List[Annotation]

    class Config:
        allow_mutation = False
        extra = "forbid"
