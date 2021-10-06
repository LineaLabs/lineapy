from datetime import datetime
from typing import Dict, Literal, Optional, List, cast, overload
from os import getcwd

from lineapy.constants import GET_ITEM, GETATTR, ExecutionMode
from lineapy.data.graph import Graph
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.lineabuiltins import __exec__, __build_tuple__
from lineapy.data.types import (
    CallNode,
    ImportNode,
    Library,
    LineaID,
    LiteralNode,
    LookupNode,
    Node,
    SessionContext,
    SessionType,
    SourceLocation,
    VariableNode,
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.execution.executor import Executor
from lineapy.instrumentation.records_manager import RecordsManager
from lineapy.instrumentation.tracer_util import (
    create_argument_nodes,
)
from lineapy.utils import (
    CaseNotHandledError,
    InternalLogicError,
    internal_warning_log,
    get_new_id,
)


class Tracer:
    def __init__(
        self,
        session_type: SessionType,
        execution_mode: ExecutionMode,
        session_name: Optional[str] = None,
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
        self.nodes_to_be_evaluated: List[Node] = []
        # TODO: we should probably poll from the local linea config file
        #   what this configuration should be
        config = get_default_config_by_environment(execution_mode)
        self.records_manager = RecordsManager(config)
        self.db = self.records_manager.db
        self.session_context = self.create_session_context(
            session_type,
            session_name,
        )
        self.executor = Executor()
        # TODO: Either save mapping of variable ID to node, or save full graph....

        self.variable_name_to_node: Dict[str, Node] = {}
        self.function_name_to_function_module_import_id: Dict[
            str, LineaID
        ] = {}

    @property
    def graph(self) -> Graph:
        # TODO: persist this instead on the tracer and keep nodes there
        nodes = self.records_manager.db.get_nodes_for_session(
            self.session_context.id
        )
        return Graph(nodes, self.session_context)

    @property
    def values(self) -> dict[str, object]:
        return self.executor._variable_values

    @property
    def stdout(self) -> str:
        return self.executor.get_stdout()

    def slice(self, artifact_name: str) -> str:
        """
        Gets the code for a slice of the graph from an artifact
        """
        artifact = self.db.get_artifact_by_name(artifact_name)
        return get_program_slice(self.graph, [LineaID(cast(str, artifact.id))])

    def add_unevaluated_node(
        self, record: Node, source_location: Optional[SourceLocation] = None
    ):
        if source_location:
            record.source_location = source_location
        self.nodes_to_be_evaluated.append(record)

    def evaluate_records_so_far(self) -> Optional[float]:
        """
        For JUPYTER & SCRIPT
        - Evaluate everything in the execution_pool
        - Pipe the records with their values to the records_manager
        - Then remove them (so that the runtime could reclaim space)
        For STATIC, same post-fix but without the evaluation
        """

        if (
            self.session_type == SessionType.SCRIPT
            or self.session_type == SessionType.JUPYTER
        ):
            # Include all the variable nodess we have as well, since
            # we could have executed some previous expressions, and then later
            # executed another one that dependened on those variables
            graph = Graph(
                self.nodes_to_be_evaluated
                + list(self.variable_name_to_node.values()),
                self.session_context,
            )

            time = self.executor.execute_program(graph)
            self.records_manager.add_evaluated_nodes(
                self.nodes_to_be_evaluated
            )
            # reset
            self.nodes_to_be_evaluated = []
            return time
        elif self.session_type == SessionType.STATIC:
            # Same flow as SCRIPT but without the executor
            # In the future, we can potentially do something fancy with
            #   importing and doing analysis there
            self.records_manager.add_evaluated_nodes(
                self.nodes_to_be_evaluated
            )
            # reset
            self.nodes_to_be_evaluated = []
            return None

        raise CaseNotHandledError(f"Case {self.session_type} is unsupported")

    def exit(self):
        self.evaluate_records_so_far()
        self.records_manager.exit()
        pass

    def lookup_node(self, variable_name: str) -> Node:
        """
        Cases:
        - user defined variable & function definitions
        - imported libs
        - unknown runtime magic functions---special case to
          LookupNode
          - builtin functions, e.g., min
          - custom runtime, e.g., get_ipython
        """
        if variable_name in self.variable_name_to_node:
            # user define var and fun def
            return self.variable_name_to_node[variable_name]
        else:
            new_node = LookupNode(
                id=get_new_id(),
                session_id=self.session_context.id,
                name=variable_name,
            )
            self.add_unevaluated_node(new_node)
            return new_node

    def look_up_node_id_by_variable_name(self, variable_name: str) -> LineaID:
        return self.lookup_node(variable_name).id

    # TODO: Refactor to take in node id
    def publish(
        self, variable_name: str, description: Optional[str] = None
    ) -> None:
        # we'd have to do some introspection here to know what the ID is
        # then we can create a new ORM node (not our IR node, which is a
        #   little confusing)
        # TODO: look up node_id base on variable_name
        # need to force an eval
        execution_time = self.evaluate_records_so_far()
        node_id = self.look_up_node_id_by_variable_name(variable_name)
        self.records_manager.add_node_id_to_artifact_table(
            node_id, description, execution_time
        )

    def create_session_context(
        self,
        session_type: SessionType,
        session_name: Optional[str],
    ):
        """
        Decided to read the code instead because it's more readable
          than passing through the transformer
        """
        working_directory = getcwd()
        session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=working_directory,
            session_name=session_name,
        )
        self.records_manager.write_session_context(session_context)
        return session_context

    def trace_import(
        self,
        name: str,
        source_location: Optional[SourceLocation] = None,
        alias: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        - `name`: the name of the module
        - `alias`: the module could be aliased, e.g., import pandas as pd
        - `attributes`: a list of functions imported from the library.
           It keys the aliased name to the original name.
        NOTE
        - The input args would _either_ have alias or attributes, but not both
        - Didn't call the function import because I think that's a protected name
        note that version and path will be introspected at runtime
        """
        library = Library(id=get_new_id(), name=name)
        node = ImportNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            alias=alias,
            library=library,
            attributes=attributes,
            source_location=source_location,
        )
        if alias is not None:
            self.variable_name_to_node[alias] = node
        else:
            self.variable_name_to_node[name] = node

        # for the attributes imported, we need to add them to the local lookup
        #  that yields the importnode's id for the `function_module` field,
        #  see `graph_with_basic_image`.
        if attributes is not None:
            for alias, original_name in attributes.items():
                # self.function_name_to_function_module_import_id[a] = node.id
                self.assign(
                    alias,
                    self.call(
                        self.lookup_node(GETATTR),
                        None,
                        node,
                        self.literal(original_name),
                    ),
                )

        # also need to modify the session_context because of weird executor
        #   requirement; should prob refactor later
        # and we cannot just modify the runtime value because
        #   it's already written to disk
        self.records_manager.add_lib_to_session_context(
            self.session_context.id, library
        )
        self.add_unevaluated_node(node)
        return

    def literal(
        self,
        value: object,
        source_location: Optional[SourceLocation] = None,
    ):
        # this literal should be assigned or used later
        node = LiteralNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            value=value,
            source_location=source_location,
        )
        self.add_unevaluated_node(node)
        return node

    def call(
        self,
        function_node: Node,
        source_location: Optional[SourceLocation],
        # function_name: str,
        *arguments: Node,
        **keyword_arguments: Node,
        # TODO: We add `CallNode` as an arg here to support nested
        # getattrs followed by a call. The "module" then is really
        # not a module, but just a CallNode that is a getattr
        # We should refactor this!
        # function_module: Union[None, str, Node] = None,
    ) -> CallNode:
        """
        NOTE
        - It's important for the call to return the call node
          so that we can programmatically chain the the nodes together,
          e.g., for the assignment call to modify the previous call node.
        - The call looks up if it's a locally defined function. We decided
          that this is better for program slicing.

        TODO:
        - the way we look up the function module is a little confusing, maybe
          decouple it from variable_name_to_id?
        """

        argument_nodes = create_argument_nodes(
            list(arguments),
            keyword_arguments,
            self.session_context.id,
        )
        argument_node_ids = []
        for n in argument_nodes:
            argument_node_ids.append(n.id)
            self.add_unevaluated_node(n)

        node = CallNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            function_id=function_node.id,
            arguments=argument_node_ids,
            source_location=source_location,
        )
        self.add_unevaluated_node(node)
        # info_log("call invoked from tracer", function_name,
        #   function_module, arguments)
        return node

    def assign(
        self,
        variable_name: str,
        value_node: Node,
        source_location: Optional[SourceLocation] = None,
    ) -> None:
        """
        Assign modifies the call node, with:
        - assigned variable name
        - the code segment for assign subsume the expression it's assigned from
          that's why we need to update
        This is not the most functional/pure but it gets the job done for now.
        """
        new_node = VariableNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            assigned_variable_name=variable_name,
            source_node_id=value_node.id,
            source_location=source_location,
        )
        self.add_unevaluated_node(new_node)
        self.variable_name_to_node[variable_name] = new_node
        return

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

    def exec(
        self,
        code: str,
        is_expression: bool,
        output_variables: list[str],
        input_values: dict[str, Node],
        source_location: Optional[SourceLocation] = None,
    ) -> Optional[Node]:
        """
        Builds a call node which will executes code statements
        with the locals set to input_values.

        For each variable in output_variables, it will create nodes which will
        assign to those local variables after calling.

        If is_expression is True, it will return the result of the expression, otherwise
        it will return None.
        """
        # make sure it's sorted so that the printer will be consistent
        output_variables.sort()
        res = self.call(
            self.lookup_node(__exec__.__name__),
            source_location,
            self.literal(code),
            self.literal(
                is_expression,
            ),
            *(self.literal(v) for v in output_variables),
            **input_values,
        )
        for i, v in enumerate(output_variables):
            self.assign(
                v,
                self.call(
                    self.lookup_node(GET_ITEM),
                    None,
                    res,
                    self.literal(i),
                ),
                source_location,
            )
        if is_expression:
            return self.call(
                self.lookup_node(GET_ITEM),
                None,
                res,
                self.literal(len(output_variables)),
            )
        return None

    def tuple(
        self, *args: Node, source_location: Optional[SourceLocation] = None
    ) -> CallNode:
        return self.call(
            self.lookup_node(__build_tuple__.__name__),
            source_location,
            *args,
        )
