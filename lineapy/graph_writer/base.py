from abc import ABC


class GraphWriter(ABC):
    """
    Base class for anything that needs to manipulate the graph
    and write some results back to the DB.
    Note that this is different from the DB writing the original nodes (e.g., CallNode from a transformer function invocation).
    TODO
    """

    pass
