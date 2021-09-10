from datetime import datetime
from typing import Dict, Any, Optional, List, cast

from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    ImportNode,
    Library,
    LineaID,
    Node,
    SessionContext,
    SessionType,
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.execution.executor import Executor
from lineapy.instrumentation.records_manager import RecordsManager
from lineapy.utils import (
    UserError,
    info_log,
    internal_warning_log,
    get_new_id,
)


# helper functions
def augment_node_with_syntax(node: Node, syntax_dictionary: Dict):
    node.lineno = syntax_dictionary["lineno"]
    node.col_offset = syntax_dictionary["col_offset"]
    node.end_lineno = syntax_dictionary["end_lineno"]
    node.end_col_offset = syntax_dictionary["end_col_offset"]


class Variable:
    def __init__(self, name: str) -> None:
        self.name = name


class Tracer:
    """
    Tracer is internal to Linea and it implements the "hidden APIs"
    that are setup by the transformer.
    """

    def __init__(
        self,
        session_type: SessionType,
        file_name: str = "",
        execution_mode: ExecutionMode = ExecutionMode.TEST,
    ):
        self.session_type = session_type
        self.file_name = file_name
        self.nodes_to_be_evaluated: List[Node] = []
        # TODO: we should probably poll from the local linea config file
        #   what this configuration should be
        config = get_default_config_by_environment(execution_mode)
        self.records_manager = RecordsManager(config)
        self.session_context = self.create_session_context(
            session_type, file_name
        )
        self.executor = Executor()
        self.variable_name_to_id: Dict[str, LineaID] = {}

    def add_unevaluated_node(
        self, record: Node, syntax_dictionary: Optional[Dict] = None
    ):
        if syntax_dictionary:
            augment_node_with_syntax(record, syntax_dictionary)
        self.nodes_to_be_evaluated.append(record)

    def evaluate_records_so_far(self):
        # going to evaluate everything in the execution_pool
        # pipe the records with their values to the records_manager
        # and then remove them (so that the runtime could reclaim space)

        if self.session_type == SessionType.JUPYTER:
            # 🔥 FIXME 🔥
            internal_warning_log(
                "The method `evaluate_records_so_far` will not evaluate"
                " correctly"
            )
        self.executor.execute_program(
            Graph(self.nodes_to_be_evaluated),
            self.session_context,
        )
        self.records_manager.add_evaluated_nodes(self.nodes_to_be_evaluated)
        # reset
        self.nodes_to_be_evaluated = []
        return

    def exit(self):
        self.evaluate_records_so_far()
        self.records_manager.exit()
        info_log("Tracer", "exit")
        pass

    def _look_up_node_id_by_variable_name(self, variable_name: str):
        if variable_name in self.variable_name_to_id:
            return self.variable_name_to_id[variable_name]

        # Note that this could also be because we didn't track
        #   variables ourselves.
        raise UserError(
            f"Trying to publish variable {variable_name}, which is not found"
        )

    def publish(
        self, variable_name: str, description: Optional[str] = None
    ) -> None:
        # we'd have to do some introspection here to know what the ID is
        # then we can create a new ORM node (not our IR node, which is a
        #   little confusing)
        # TODO: look up node_id base on variable_name
        # need to force an eval
        self.evaluate_records_so_far()
        node_id = self._look_up_node_id_by_variable_name(variable_name)
        self.records_manager.add_node_id_to_artifact_table(node_id, description)

    def create_session_context(self, session_type: SessionType, file_name: str):
        """
        Decided to read the code instead because it's more readable than passing
          through the transformer
        """
        lines = open(file_name, "r").readlines()
        original_code = "".join(lines)
        session_context = SessionContext(
            id=get_new_id(),
            # TODO: hm, we should prob refactor the name, kinda confusing here
            environment_type=session_type,
            creation_time=datetime.now(),
            file_name=file_name,
            code=original_code,
        )
        self.records_manager.write_session_context(session_context)
        return session_context

    def trace_import(
        self,
        name: str,
        syntax_dictionary: Dict,
        alias: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        didn't call it import because I think that's a protected name
        note that version and path will be introspected at runtime
        """
        library = Library(id=get_new_id(), name=name)
        node = ImportNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            alias=alias,
            library=library,
            attributes=attributes,
        )
        info_log("creating", name, alias, attributes, syntax_dictionary)
        self.add_unevaluated_node(node, syntax_dictionary)
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

    def call(
        self,
        function_name: str,
        arguments: Any,
        syntax_dictionary: Dict,
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
                    session_id=self.session_context.id,
                    value_literal=a,
                    positional_order=idx,
                )
                self.add_unevaluated_node(new_literal_arg)
                argument_nodes.append(new_literal_arg.id)
            elif type(a) is CallNode:
                info_log("argument is call", a)
                new_call_arg = ArgumentNode(
                    id=get_new_id(),
                    session_id=self.session_context.id,
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
            session_id=self.session_context.id,
            function_name=function_name,
            arguments=argument_nodes,
            function_module=function_module,
        )
        self.add_unevaluated_node(node, syntax_dictionary)
        # info_log("call invoked from tracer", function_name, function_module, arguments)
        return node

    def assign(
        self,
        variable_name: str,
        value_node: Any,
        syntax_dictionary: Dict,
    ):
        """
        Assign modifies the call node. This is not the most functional/pure
          but it gets the job done.
        TODO: add support for other types of assignment
        """
        if type(value_node) is CallNode:
            call_node = cast(CallNode, value_node)
            call_node.assigned_variable_name = variable_name
            # the assignment subsumes the original call code
            augment_node_with_syntax(call_node, syntax_dictionary)
            self.variable_name_to_id[variable_name] = call_node.id
        else:
            internal_warning_log("got type", type(value_node), value_node)
            raise NotImplementedError

    def loop(self) -> None:
        """
        Handles both for and while loops. Since we are treating it like a black
          box, we don't really need to know much about it at this point

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
