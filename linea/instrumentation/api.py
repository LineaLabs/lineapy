from linea.dataflow import records_pool
from linea.dataflow.data_types import Node, DirectedEdge


def assign() -> None:
    """
    TODO: define input arguments

    TODO: append records (Node and DirectedEdge) to records_pool
    :return:
    """
    pass


def call() -> None:
    """
    TODO: define input arguments

    TODO: append records (Node and DirectedEdge) to records_pool
    """
    pass


def loop() -> None:
    """
    Handles both for and while loops.

    TODO: define input arguments

    TODO: append records (Node and DirectedEdge) to records_pool
    """
    pass
    pass


def cond() -> None:
    """
    TODO: define input arguments

    TODO: append records (Node and DirectedEdge) to records_pool
    """
    pass


def func() -> None:
    """
    TODO: define input arguments

    TODO: append records (Node and DirectedEdge) to records_pool
    """
    pass


class tracking:
    """
    with linea.tracking('docs_training'):
        ...
    """

    def __init__(self, session_name: str):
        self.session_name = session_name
        # TODO

    def __enter__(self):
        """
        TODO: set up the tracking context.
        """
        pass

    def __exit__(self):
        """
        TODO: shut down tracking services.
        """
        pass
