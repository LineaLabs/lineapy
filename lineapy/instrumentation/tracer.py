from typing import Dict
from webbrowser import get
from tests.util import get_new_id
from lineapy.utils import info_log, internal_warning_log
from lineapy.instrumentation.records_manager import RecordsManager
from typing import Any, List, Optional, Union
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    ImportNode,
    Library,
    Node,
    DirectedEdge,
    SessionType,
)


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

    TRACE_IMPORT = "trace_import"

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

    TRACE_CALL = "call"

    def call(
        self,
        function_name: str,
        arguments: Any,
        function_module: Optional[str] = None,
    ) -> CallNode:
        """
        TODO:
        - code: str
        - need to look up the function module live to get the ID

        """

        # info_log("tracel call", function_name, code, function_module)
        argument_nodes = []
        for a in arguments:
            if type(a) is int or str:
                new_literal_arg = ArgumentNode(
                    id=get_new_id(),
                    session_id=self.session_id,
                    value_literal=a,
                )
                self.records_manager.add_node(new_literal_arg)
                argument_nodes.append(new_literal_arg.id)
            elif type(a) is CallNode:
                new_call_arg = ArgumentNode(
                    id=get_new_id(), session_id=self.session_id, value_node_id=a.id
                )
                self.records_manager.add_node(new_call_arg)
                argument_nodes.append(new_call_arg.id)
            else:
                # internal_warning_log()
                raise NotImplementedError(type(a), "not supported!")

        new_id = get_new_id()

        node = CallNode(
            id=new_id,
            session_id=self.session_id,
            code="",
            function_name=function_name,
            arguments=argument_nodes,
            function_module=function_module,
        )

        self.records_manager.add_node(node)
        # info_log("call invoked from tracer", function_name, function_module, arguments)
        return node

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
