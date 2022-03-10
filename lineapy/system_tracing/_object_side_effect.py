from dataclasses import dataclass
from typing import List, Union


@dataclass
class ViewOfObject:
    objects: List[object]


@dataclass
class MutatedObject:
    object: object


@dataclass
class ImplicitDependencyObject:
    object: object


ObjectSideEffect = Union[ViewOfObject, MutatedObject, ImplicitDependencyObject]
