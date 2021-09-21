from datetime import datetime
from typing import Dict, Any, Optional, List, cast

from lineapy.constants import ExecutionMode
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    FunctionDefinitionNode,
    ImportNode,
    Library,
    LineaID,
    LiteralNode,
    Node,
    SessionContext,
    SessionType,
    VariableNode,
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.execution.executor import Executor
from lineapy.instrumentation.records_manager import RecordsManager
from lineapy.instrumentation.tracer_util import (
    ARGS_TYPE,
    KEYWORD_ARGS_TYPE,
    create_argument_nodes,
)
from lineapy.utils import (
    CaseNotHandledError,
    InternalLogicError,
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


class Tracer:
    def __init__(
        self,
        session_type: SessionType,
        file_name: str = "",
        execution_mode: ExecutionMode = ExecutionMode.TEST,
    ):
        """
        Tracer is internal to Linea and it implements the "hidden APIs"
          that are setup by the transformer.
        It performs the following key functionalities:
        - Creates the graph nodes and inserts into the database.
        - Maintains data structures to help creating the graph IR
          that is used later, which includes:
          - `variable_name_to_id`: for tracking variable/function/module
            to the ID responsible for its creation
        - Executes the program, using the `Executor`.
        """
        self.session_type = session_type
        self.file_name = file_name
        self.nodes_to_be_evaluated: List[Node] = []
        # TODO: we should probably poll from the local linea config file
        #   what this configuration should be
        config = get_default_config_by_environment(execution_mode)
        self.records_manager = RecordsManager(config)
        self.session_context = self.create_session_context(
            session_type,
            file_name,
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
        """
        For JUPYTER & SCRIPT
        - Evaluate everything in the execution_pool
        - Pipe the records with their values to the records_manager
        - Then remove them (so that the runtime could reclaim space)
        For STATIC, same post-fix but without the evaluation
        """

        if self.session_type == SessionType.JUPYTER:
            # 🔥 FIXME 🔥
            internal_warning_log(
                "The method `evaluate_records_so_far` will not evaluate"
                " correctly"
            )
            return

        elif self.session_type == SessionType.SCRIPT:
            self.executor.execute_program(
                Graph(self.nodes_to_be_evaluated),
                self.session_context,
            )
            self.records_manager.add_evaluated_nodes(
                self.nodes_to_be_evaluated
            )
            # reset
            self.nodes_to_be_evaluated = []
            return
        elif self.session_type == SessionType.STATIC:
            # Same flow as SCRIPT but without the executor
            # In the future, we can potentially do something fancy with
            #   importing and doing analysis there
            self.records_manager.add_evaluated_nodes(
                self.nodes_to_be_evaluated
            )
            # reset
            self.nodes_to_be_evaluated = []
            return

        raise CaseNotHandledError(f"Case {self.session_type} is unsupported")

    def exit(self):
        self.evaluate_records_so_far()
        self.records_manager.exit()
        info_log("Tracer exit")
        pass

    def look_up_node_id_by_variable_name(
        self,
        variable_name: str,
    ) -> LineaID:
        if variable_name in self.variable_name_to_id:
            return self.variable_name_to_id[variable_name]

        # Note that this could also be because we didn't track
        #   variables ourselves.
        raise UserError(
            f"Trying to lookup variable {variable_name}, which is not"
            " found. Note that this could be that you are trying to publish a"
            " variable assigned to a literal value."
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
        node_id = self.look_up_node_id_by_variable_name(variable_name)
        self.records_manager.add_node_id_to_artifact_table(
            node_id,
            description,
        )

    def create_session_context(
        self,
        session_type: SessionType,
        file_name: str,
    ):
        """
        Decided to read the code instead because it's more readable
          than passing through the transformer
        """
        original_code = open(file_name, "r").read()
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
        syntax_dictionary: Dict[str, int],
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
        if alias is not None:
            self.variable_name_to_id[alias] = node.id
        else:
            self.variable_name_to_id[name] = node.id
        self.add_unevaluated_node(node, syntax_dictionary)
        return

    def headless_variable(
        self, variable_name: str, syntax_dictionary: Dict[str, int]
    ) -> None:
        source_node_id = self.look_up_node_id_by_variable_name(variable_name)
        if source_node_id is not None:
            node = VariableNode(
                id=get_new_id(),
                session_id=self.session_context.id,
                source_variable_id=source_node_id,
            )
            # FIXME: this node doesn't even need to be evaluated
            #   we should prob decouple the evaluation with the insertion
            #   of new nodes
            self.add_unevaluated_node(node, syntax_dictionary)
        else:
            raise InternalLogicError(f"Variable {variable_name} not found")

    def headless_literal(
        self, value: Any, syntax_dictionary: Dict[str, int]
    ) -> None:
        """ """
        node = LiteralNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            value=value,
        )
        self.add_unevaluated_node(node, syntax_dictionary)

    def literal(
        self,
        value: Any,
        assigned_variable_name: Optional[str],
        syntax_dictionary: Dict[str, int],
    ):
        # this literal should be assigned or used later
        node = LiteralNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            value=value,
            assigned_variable_name=assigned_variable_name,
        )
        if assigned_variable_name is not None:
            self.variable_name_to_id[assigned_variable_name] = node.id
        self.add_unevaluated_node(node, syntax_dictionary)

    def call(
        self,
        function_name: str,
        arguments: ARGS_TYPE,
        keyword_arguments: KEYWORD_ARGS_TYPE,
        syntax_dictionary: Dict[str, int],
        function_module: Optional[Any] = None,
    ) -> CallNode:
        """
        NOTE
        - It's important for the call to return the call node
          so that we can programmatically chain the the nodes together,
          e.g., for the assignment call to modify the previous call node.
        - The call looks up if it's a locally defined function. We decided
          that this is better for program slicing.

        TODO:
        - need to look up the function module live to get the ID
        """

        argument_nodes = create_argument_nodes(
            arguments,
            keyword_arguments,
            self.session_context.id,
            self.look_up_node_id_by_variable_name,
        )
        argument_node_ids = [n.id for n in argument_nodes]
        [self.add_unevaluated_node(n) for n in argument_nodes]

        locally_defined_function_id: Optional[LineaID] = None
        # now see if we need to add a locally_defined_function_id
        if function_name in self.variable_name_to_id:
            locally_defined_function_id = self.variable_name_to_id[
                function_name
            ]

        # Get node id for function module
        if function_module is not None:
            function_module = self.variable_name_to_id[function_module]

        node = CallNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            function_name=function_name,
            locally_defined_function_id=locally_defined_function_id,
            arguments=argument_node_ids,
            function_module=function_module,
        )
        self.add_unevaluated_node(node, syntax_dictionary)
        # info_log("call invoked from tracer", function_name,
        #   function_module, arguments)
        return node

    def assign(
        self,
        variable_name: str,
        value_node: Any,
        syntax_dictionary: Dict,
    ):
        """
        Assign modifies the call node, with:
        - assigned variable name
        - the code segment for assign subsume the expression it's assigned from
          that's why we need to update
        This is not the most functional/pure but it gets the job done for now.
        """
        # shared logic
        self.variable_name_to_id[variable_name] = value_node.id
        augment_node_with_syntax(value_node, syntax_dictionary)
        if type(value_node) is CallNode:
            call_node = cast(CallNode, value_node)
            call_node.assigned_variable_name = variable_name
        elif type(value_node) in [VariableNode, LiteralNode]:
            pass  # shared logic is sufficient
        elif type(value_node) in [int, str]:
            # hack: we should have consistent Literal handling...
            new_node = LiteralNode(
                id=get_new_id(),
                session_id=self.session_context.id,
                assigned_variable_name=variable_name,
                value=value_node,
            )
            self.add_unevaluated_node(new_node)
            self.variable_name_to_id[variable_name] = new_node.id
            return
        else:
            raise CaseNotHandledError(
                f"got type {type(value_node)} for {value_node}"
            )

    def define_function(
        self,
        function_name: str,
        syntax_dictionary: Dict,
    ) -> None:
        """
        TODO: see limitations in `visit_FunctionDef` about function being pure
        """
        node = FunctionDefinitionNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            function_name=function_name,
        )
        self.variable_name_to_id[function_name] = node.id
        self.add_unevaluated_node(node, syntax_dictionary)

    def loop(self) -> None:
        """
        Handles both for and while loops. Since we are treating it like a black
          box, we don't really need to know much about it at this point

        TODO: define input arguments

        TODO: append records
        """
        pass

    def cond(self) -> None:
        """
        TODO: define input arguments

        TODO: append records
        """
        pass
