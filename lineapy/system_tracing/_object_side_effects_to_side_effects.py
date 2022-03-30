import logging
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

logger = logging.getLogger(__name__)

# Mapping of the ID of each external state object to its pointer
EXTERNAL_STATE_IDS: Dict[int, ExecutorPointer] = {
    id(b): b for b in LINEA_BUILTINS.values() if isinstance(b, ExternalState)
}


def object_side_effects_to_side_effects(
    object_side_effects: Iterable[ObjectSideEffect],
    input_nodes: Mapping[LineaID, object],
    output_globals: Mapping[str, object],
) -> Iterable[SideEffect]:
    """
    Translates a list of object side effects to a list of side effects, by
    mapping objects to nodes, and only emitting side effects
    that references only input nodes or the output globals.

    The process is not just trimming off internal variables, but also sometimes
    transitively searching for nodes. Consider the following example:
    ```python
    y = 10
    if ...:
        z = [y]
        a = [z]
        del z
    ```
    We want to establish that `a` is a view of `y`, and skip z because it's not in
    the outer scope that we care about.

    :param object_side_effects: The object side effects that were recorded.
    :param input_nodes: Mapping of node ID to value for all the nodes that were passed in to this execution.
    :param output_globals: Mapping of global identifier to the value of all globals that were set during this execution.
    """
    # First track all the views and mutations in terms of objects
    #   (no Nodes reference)
    tracker = ObjectMutationTracker()
    for i, object_side_effect in enumerate(object_side_effects):
        tracker.process_side_effect(object_side_effect)

    # Mapping of object ids for the objects we care about, input nodes &
    #   external state, to the `ExecutorPointer` to them.
    # One object ID can have multiple pointers, for example, when we have an
    # alias:
    # ```y = [1]
    # b = y
    # ```
    logger.debug("Creating list of objects we care about")

    object_id_to_pointers: Dict[int, List[ExecutorPointer]] = defaultdict(list)
    for object_id, pointer in EXTERNAL_STATE_IDS.items():
        object_id_to_pointers[object_id].append(pointer)
    for linea_id, obj in input_nodes.items():
        object_id_to_pointers[id(obj)].append(ID(LineaID(linea_id)))

    logger.debug("Returning implicit dependencies")

    for id_ in tracker.implicit_dependencies:
        for pointer in object_id_to_pointers[id_]:
            yield ImplicitDependencyNode(pointer)

    logger.debug("Returning mutated nodes")
    for id_ in tracker.mutated:
        for pointer in object_id_to_pointers[id_]:
            yield MutatedNode(pointer)

    logger.debug("Returning views")

    # For the views, we care about whether they include the outputs as well,
    # so lets add those to the objects we care about
    for name, value in output_globals.items():
        object_id_to_pointers[id(value)].append(Variable(name))

        # Also add these as empty views, so they are processed if there are
        # are multiple pointers for this id
        tracker.viewers[id(value)]
    # ID of objects we have already emitted views for
    processed_view_ids: Set[int] = set()
    # We iterate through all the sets of viewers we have recorded, and for each viewer set, look up all object
    # pointers related to it and emit a view if we have more than one.
    for id_, views in tracker.viewers.items():
        if id_ in processed_view_ids:
            continue
        processed_view_ids.add(id_)
        # subset of view that we care about
        pointers = object_id_to_pointers[id_]
        # Find all the objects that we care about and add them
        for view_id in views:
            processed_view_ids.add(view_id)
            pointers.extend(object_id_to_pointers[view_id])
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
            # Special case for two objects, which is most calls, to speed up processing
            if len(object_side_effect.objects) == 2:
                l_obj, r_obj = object_side_effect.objects
                l_id = id(l_obj)
                r_id = id(r_obj)
                if l_id == r_id:
                    return
                l_viewers = self.viewers[l_id]
                r_viewers = self.viewers[r_id]

                already_viewers = l_id in r_viewers
                if already_viewers:
                    return

                # Since they are not views of each other, we know that their viewers are mutually exclusive, so to find
                # the intersection we can just combine them both and not worry about duplicates
                l_viewers_copy = list(l_viewers)
                l_viewers.extend(r_viewers)
                l_viewers.append(r_id)

                r_viewers.extend(l_viewers_copy)
                r_viewers.append(l_id)

            else:
                ids = [id(o) for o in object_side_effect.objects]
                set_as_viewers_generic(ids, self.viewers)

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
