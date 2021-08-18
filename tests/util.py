from datetime import datetime
from lineapy.data.graph import Graph
from uuid import uuid4

from lineapy.data.types import (
    Node,
    SessionContext,
    SessionType,
)


def get_new_id():
    return uuid4()


def get_new_session():
    return SessionContext(
        uuid=get_new_id(),
        file_name="testing.py",
        environment_type=SessionType.SCRIPT,
        creation_time=datetime.now(),
    )


def are_nodes_equal(n1: Node, n2: Node, deep_check=False) -> bool:
    """
    - If deep_check is True, check each field of the nodes, otherwise, just check the ID.
    - deep_check is useful for testing
    """
    # first check if they are the same type
    if n1.id != n2.id:
        return False
    if deep_check:
        if n1.node_type != n2.node_type:
            return False
        # @dhruv TODO: then based on each node type do some custom testing
        # Maybe there is an easier way to just implement their __str__ and check that?
    return True


def are_graph_equal(g1: Graph, g2: Graph) -> bool:
    raise NotImplementedError
