from typing import Optional

from lineapy.instrumentation.records_manager import RecordsManager
from lineapy.utils import info_log


class Tracer:
    """
    Tracer is internal to Linea and it implements the "hidden APIs" that are setup by the transformer.
    """

    def __init__(self, session_name: Optional[str]):
        self.session_name = session_name
        self.records_manager = RecordsManager()

    def exit(self):
        info_log("Tracer", "exit")
        pass

    def publish(self, variable_name: str, description: Optional[str]) -> None:
        # we'd have to do some introspection here to know what the ID is
        # then we can create a new ORM node (not our IR node, which is a little confusing)
        pass

    def literal(self) -> None:
        """
        For the following cases
        ```
        1
        a = 1
        ```
        Corresponds to the `LiteralNode`
        TODO:
        - [ ] define input arguments
        = [ ] make sure that all the
        """
        pass

    def variable(self) -> None:
        """
        For the following cases
        ```
        a
        b=a
        ```
        Corresponds to the `VariableNode`
        """

    def call(self) -> None:
        """
        TODO:
        - [ ] define input arguments
        - [ ] append records (Node and DirectedEdge) to `records_pool`

        """
        pass

    def loop(self) -> None:
        """
        Handles both for and while loops. Since we are trating it like a black box, we don't really need to know mucha bout it at this point

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
