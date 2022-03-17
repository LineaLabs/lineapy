from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import Dict, Iterable, List, Tuple, TypeVar

from lineapy.data.types import LineaID
from lineapy.utils.utils import get_new_id, remove_duplicates, remove_value


@dataclass
class MutationTracker:

    ##
    # We store information on two types of relationships between nodes:
    #
    # 1. Source -> Mutate nodes, which is a directed relationship meaning
    #    whenever a new node is created that refers to the source node, it
    #    instead should refer to the mutate node.
    # 2. Undirected view relationships. If two nodes are a view of each other,
    #    they a mutating one may mutate the other, so if one is mutated, mutate
    #    nodes need to be made for all the other nodes that are views. This is
    #    a transitive relationship.
    #
    # We use lists in the data structures to store these relationships, but no
    # entry should repeat. Ordering is not important for correctness
    # but for having deterministic node ordering, which is needed for
    # deterministic snapshot generation and comparison.
    ##

    # Mapping of mutated nodes, from their original node id, to the immediate
    # mutate node id they are the source of
    # a = []       CallNode ID: i1
    # a.append(1)  MutateNodeID: i2
    # a.append(2)  MutateNodeID: i3
    # source_to_mutate = {i1: i2, i2: i3}
    source_to_mutate: Dict[LineaID, LineaID] = field(default_factory=dict)

    # Mapping from each node to every node which has a view of it,
    # meaning that if that node is mutated, the view node will be as well
    # a = []    CallNode ID: i1
    # b = [a]   CallNode ID: i2
    # c = [b]   CallNode ID: i3
    # viewers: {i1: [i2, i3], i2: [i1, i3], i3: [i1, i2]}
    # NOTE that b = a would not constitute a view relationship
    viewers: Dict[LineaID, List[LineaID]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def set_as_viewers_of_eachother(self, *ids: LineaID) -> None:
        """
        To process adding views between nodes, update the `viewers` data structure
        with all new viewers.
        """
        return set_as_viewers_generic(list(ids), self.viewers)

    def get_latest_mutate_node(self, node_id: LineaID) -> LineaID:
        """
        Find the latest mutate node, that refers to it.
        Call this before creating a object based on another node.
        """
        # Keep looking up to see if their is a new mutated version of this
        # node
        while node_id in self.source_to_mutate:
            node_id = self.source_to_mutate[node_id]
        return node_id

    def set_as_mutated(
        self, source_id: LineaID
    ) -> Iterable[Tuple[LineaID, LineaID]]:
        """
        To process mutating a node, we create new mutate nodes for each views of
        this node and update the source to view mapping to point to the new nodes.
        """
        # Create a mutation node for every node that was mutated,
        # Which are all the views + the node itself
        # Note: must resolve generator before iterating, so that get_latest_mutate_node
        # is called eagerly, otherwise we end up with duplicate mutate nodes.
        source_ids = list(
            remove_duplicates(
                map(
                    self.get_latest_mutate_node,
                    [*self.viewers[source_id], source_id],
                )
            )
        )
        for source_id in source_ids:
            mutate_node_id = get_new_id()

            # First we update the forward mapping, mapping them to the new mutate node
            self.source_to_mutate[source_id] = mutate_node_id

            yield mutate_node_id, source_id


T = TypeVar("T")


def set_as_viewers_generic(ids: List[T], viewers: Dict[T, List[T]]) -> None:
    """
    Generic version of method, so that we can use it in the settrace tracker as well
    """
    # First, iterate through all items in the view
    # and create a complete view set adding all their views as well
    # since it is a transitivity relationionship.
    complete_ids = list(
        remove_duplicates(chain(ids, *(viewers[id_] for id_ in ids)))
    )

    # Now update the viewers data structure to include all the viewers,
    # apart the id itself, which is not kept in the mapping.
    for id_ in complete_ids:
        viewers[id_] = list(remove_value(complete_ids, id_))
