"""
These classes represent side effects, where the values are actual
Python object, in comparison to the other two representations,
where the values are either references to a certain argument (i.e. the first arg)
or to a node.
"""
from dataclasses import dataclass
from typing import List, Union


@dataclass
class ViewOfObjects:
    objects: List[object]


@dataclass
class MutatedObject:
    object: object


@dataclass
class ImplicitDependencyObject:
    object: object


ObjectSideEffect = Union[
    ViewOfObjects, MutatedObject, ImplicitDependencyObject
]
