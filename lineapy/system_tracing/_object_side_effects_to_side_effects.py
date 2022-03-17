from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Set

from lineapy.data.types import LineaID
from lineapy.execution.side_effects import (
    ID,
    ExecutorPointer,
    ImplicitDependencyNode,
    MutatedNode,
    SideEffect,
    Variable,
    ViewOfNodes,
)
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.instrumentation.mutation_tracker import set_as_viewers_generic
from lineapy.system_tracing._object_side_effect import (
    ImplicitDependencyObject,
    MutatedObject,
    ObjectSideEffect,
    ViewOfObjects,
)
from lineapy.utils.lineabuiltins import LINEA_BUILTINS

# Mapping of the ID of each external state object to its pointer
EXTERNAL_STATE_IDS: Dict[int, ExternalState] = {
    id(b): b for b in LINEA_BUILTINS.values() if isinstance(b, ExternalState)
}


# TODO: Add unit tests for all parts of this...
def object_side_effects_to_side_effects(
    object_side_effects: Iterable[ObjectSideEffect],
    input_nodes: Mapping[LineaID, object],
    output_globals: Mapping[str, object],
) -> Iterable[SideEffect]:
    """
    Translates a list of object side effects to a list of side effects, by mapping objects to nodes, and only emitting side effects
    which relate to either the input nodes or the output globals.

    :param object_side_effects: The object side effects that were recorded.
    :param input_nodes: Mapping of node ID to value for all the nodes that were passed in to this execution.
    :param output_globals: Mapping of global identifier to the value of all globals that were set during this execution.
    """
    tracker = ObjectMutationTracker()

    for object_side_effect in object_side_effects:
        tracker.process_side_effect(object_side_effect)

    # mapping of object ids for the objects we care about, input nodes as well as external state, to the pointer to them
    object_id_to_pointer: Dict[int, ExecutorPointer] = {
        id(obj): ID(linea_id) for linea_id, obj in input_nodes.items()
    }
    object_id_to_pointer.update(EXTERNAL_STATE_IDS)

    # Return all implicit dependencies
    for id_ in tracker.implicit_dependencies:
        if id_ in object_id_to_pointer:
            yield ImplicitDependencyNode(object_id_to_pointer[id_])

    # Return all mutated nodes
    for id_ in tracker.mutated:
        if id_ in object_id_to_pointer:
            yield MutatedNode(object_id_to_pointer[id_])

    # Return all views
    # For the views, we care about whether they include the ouputs as well, so lets add those to the objects we care about
    object_id_to_pointer.update(
        {id(value): Variable(name) for name, value in output_globals.items()}
    )
    # ID of objects we have already emitted views for
    processed_view_ids: Set[int] = set()
    for id_, views in tracker.viewers.items():
        if id_ in processed_view_ids:
            continue
        processed_view_ids.add(id_)
        if id_ in object_id_to_pointer:
            # subset of view that we care about
            pointers = [object_id_to_pointer[id_]]
            # Find all the objects that we care about and add them
            for view_id in views:
                processed_view_ids.add(view_id)
                if view_id in object_id_to_pointer:
                    pointers.append(object_id_to_pointer[view_id])
            if len(pointers) > 1:
                yield ViewOfNodes(pointers)


@dataclass
class ObjectMutationTracker:
    """
    Keeps track of all views and mutations of objects, after a number of view or mutation operations, by using object ID
    as the unique ID.

    Similar in spirit to the mutation_tracker used by the tracer, but has a slightly different scope, since here we are
    dealing with Python objects, not linea nodes, and we only care about the composite operations, not every one.
    """

    # Mapping from each object ID to the list of other objects that have views of it and vice versa.
    # The relationship is symmetric, so if a and b are views of one another, the ID of a, will have the ID of b in it,
    # and vice versa.
    # The values are unique, but we used a list to preserve ordering for tests
    viewers: Dict[int, List[int]] = field(
        default_factory=lambda: defaultdict(list)
    )
    # All the objects that have been mutated, directly or indirectly.
    # This also should be a set, but using a list for preserved ordering
    mutated: List[int] = field(default_factory=list)

    # List of objects which have implicit dependencies
    implicit_dependencies: List[int] = field(default_factory=list)

    def process_side_effect(
        self, object_side_effect: ObjectSideEffect
    ) -> None:
        if isinstance(object_side_effect, ViewOfObjects):
            set_as_viewers_generic(
                [id(o) for o in object_side_effect.objects], self.viewers
            )
        elif isinstance(object_side_effect, MutatedObject):
            id_ = id(object_side_effect.object)
            self.add_mutated(id_)
            for v in self.viewers[id_]:
                self.add_mutated(v)
        elif isinstance(object_side_effect, ImplicitDependencyObject):
            self.add_implicit_dependency(id(object_side_effect.object))

    def add_mutated(self, id_: int) -> None:
        if id_ not in self.mutated:
            self.mutated.append(id_)

    def add_implicit_dependency(self, id_: int) -> None:
        if id_ not in self.implicit_dependencies:
            self.implicit_dependencies.append(id_)
