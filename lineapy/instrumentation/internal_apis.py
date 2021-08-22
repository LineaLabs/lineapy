from typing import Any, List, Union
from lineapy.data.types import Node, DirectedEdge


class Tracer:
    """
    The way that we expect users to use linea is:
    ```
    import lineapy
    ln = lineapy.start()
    # ... their code
    #
    ln.save(variable_name)
    ```
    """

    def __init__(self, session_name: str):
        self.session_name = session_name
        # TODO

    def save(self, variable: Any) -> None:
        # we'd have to do some introspection here to know what it is.
        #
        pass

    def assign(self) -> None:
        """
        TODO:
        - [ ] define input arguments
        - [ ] append records (Node and DirectedEdge) to `records_pool`
        = [ ] make sure that all the
        """
        pass

    def call(self) -> None:
        """
        TODO: define input arguments

        TODO: append records (Node and DirectedEdge) to records_pool

        TODO:
        """
        pass

    def loop(self) -> None:
        """
        Handles both for and while loops.

        TODO: define input arguments

        TODO: append records (Node and DirectedEdge) to records_pool
        """
        pass

    def cond(self) -> None:
        """
        TODO: define input arguments

        TODO: append records (Node and DirectedEdge) to records_pool
        """
        pass

    def func(self) -> None:
        """
        TODO: define input arguments

        TODO: append records (Node and DirectedEdge) to records_pool
        """
        pass
