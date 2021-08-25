from typing import Dict
from tests.util import get_new_id
from lineapy.utils import info_log
from lineapy.instrumentation.records_manager import RecordsManager
from typing import Any, List, Optional, Union
from lineapy.data.types import ImportNode, Library, Node, DirectedEdge, SessionType


class Tracer:
    """
    Tracer is internal to Linea and it implements the "hidden APIs" that are setup by the transformer.
    """

    def __init__(self, environment_type: str, file_name: Optional[str]):
        # TODO map to SessionType
        self.environment_type = environment_type
        self.file_name = file_name
        self.records_manager = RecordsManager()
        self.session_id = get_new_id()

    def exit(self):
        info_log("Tracer", "exit")
        pass

    def publish(self, variable_name: str, description: Optional[str]) -> None:
        # we'd have to do some introspection here to know what the ID is
        # then we can create a new ORM node (not our IR node, which is a little confusing)
        pass

    def create_session_context(self):
        pass

    def trace_import(
        self,
        name: str,
        code: str,
        alias: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        didn't call it import because I think that's a protected name
        """
        library = Library(
            name=name
            # note that version and path will be instrospected at runtime
        )
        info_log("creating", name, code, alias, attributes)
        node = ImportNode(
            id=get_new_id(),
            session_id=self.session_id,
            code=code,
            alias=alias,
            library=library,
            attributes=attributes,
        )
        self.records_manager.add_node(node)
        return

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
