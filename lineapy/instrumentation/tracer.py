from datetime import datetime
from typing import Dict, Any, Optional, List, cast

from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    ImportNode,
    Library,
    Node,
    SessionContext,
    SessionType,
)
from lineapy.execution.executor import Executor
from lineapy.instrumentation.instrumentation_util import (
    get_linea_db_config_from_execution_mode,
)
from lineapy.instrumentation.records_manager import RecordsManager
from lineapy.utils import info_log, internal_warning_log, get_new_id


class Tracer:
    """
    Tracer is internal to Linea and it implements the "hidden APIs" that are setup by the transformer.
    """

    def __init__(
        self,
        session_type: SessionType,
        file_name: str = "",
        execution_mode: ExecutionMode = ExecutionMode.TEST,
    ):
        self.session_type = session_type
        self.file_name = file_name
        self.execution_pool: List[Node] = []
        # TODO: we should probably poll from the local linea config file what this configuration should be
        config = get_linea_db_config_from_execution_mode(execution_mode)
        self.records_manager = RecordsManager(config)
        self.session_id = get_new_id()
        self.executor = Executor()
        self.create_session_context(session_type, file_name)

    def add_unevaluated_node(self, record: Node):
        self.execution_pool.append(record)

    def evaluate_records_so_far(self):
        # going to evaluate everything in the execution_pool
        # pipe the records with their values to the records_manager
        # and then remove them (so that the runtime could reclaim space)

        if self.session_type == SessionType.JUPYTER:
            # 🔥 FIXME 🔥
            internal_warning_log(
                "The method `evaluate_records_so_far` will not evaluate correctly"
            )
        self.executor.execute_program(Graph(self.execution_pool))
        self.records_manager.add_evaluated_nodes(self.execution_pool)
        # reset
        self.execution_pool = []
        return

    def exit(self):
        self.evaluate_records_so_far()
        self.records_manager.exit()
        info_log("Tracer", "exit")
        pass

    def publish(self, variable_name: str, description: Optional[str]) -> None:
        # we'd have to do some introspection here to know what the ID is
        # then we can create a new ORM node (not our IR node, which is a little confusing)
        pass

    def create_session_context(self, session_type: SessionType, file_name: str):
        session_context = SessionContext(
            id=self.session_id,
            # TODO: hm, we should prob refactor the name, kinda confusing here
            environment_type=session_type,
            creation_time=datetime.now(),
            file_name=file_name,
        )
        self.records_manager.write_session_context(session_context)

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
            id=get_new_id(),
            name=name
            # note that version and path will be instrospected at runtime
        )
        node = ImportNode(
            id=get_new_id(),
            session_id=self.session_id,
            code=code,
            alias=alias,
            library=library,
            attributes=attributes,
        )
        info_log("creating", name, code, alias, attributes)
        self.add_unevaluated_node(node)
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
        code: str,
        function_module: Optional[str] = None,
    ) -> CallNode:
        """
        Note that it's important for the call to return the call node so that we can programmatically chain the the nodes together, e.g., for the assignment call to modify the previous call node.

        TODO:
        - code: str
        - need to look up the function module live to get the ID

        """

        info_log("arguments", arguments)
        argument_nodes = []
        for idx, a in enumerate(arguments):
            info_log("type of arg", type(a))
            if type(a) is int or type(a) is str:
                info_log("argument is literal", a)
                new_literal_arg = ArgumentNode(
                    id=get_new_id(),
                    session_id=self.session_id,
                    value_literal=a,
                    positional_order=idx,
                )
                self.add_unevaluated_node(new_literal_arg)
                argument_nodes.append(new_literal_arg.id)
            elif type(a) is CallNode:
                info_log("argument is call", a)
                new_call_arg = ArgumentNode(
                    id=get_new_id(),
                    session_id=self.session_id,
                    value_node_id=a.id,
                    positional_order=idx,
                )
                self.add_unevaluated_node(new_call_arg)
                argument_nodes.append(new_call_arg.id)
            else:
                internal_warning_log("haven't seen this argument before!")
                raise NotImplementedError(type(a), "not supported!")

        node = CallNode(
            id=get_new_id(),
            session_id=self.session_id,
            code=code,
            function_name=function_name,
            arguments=argument_nodes,
            function_module=function_module,
        )

        self.add_unevaluated_node(node)
        # info_log("call invoked from tracer", function_name, function_module, arguments)
        return node

    TRACE_ASSIGN = "assign"

    def assign(self, variable_name: str, value_node: Any, code: str):
        """
        Assign modifies the call node. This is not the most functional but it gets the job done.
        TODO: add support for other types of assignment
        """
        if type(value_node) is CallNode:
            call_node = cast(CallNode, value_node)
            call_node.assigned_variable_name = variable_name
            # the assignment subsumes the original call code
            call_node.code = code
        else:
            internal_warning_log("got type", type(value_node), value_node)
            raise NotImplementedError

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
