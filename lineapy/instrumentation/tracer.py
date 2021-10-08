import logging
from datetime import datetime
from os import getcwd
from typing import Dict, Optional, cast

from lineapy.constants import GET_ITEM, GETATTR, ExecutionMode
from lineapy.data.graph import Graph
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
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import get_program_slice
from lineapy.instrumentation.inspect_function import inspect_function
from lineapy.instrumentation.records_manager import RecordsManager
from lineapy.lineabuiltins import __build_tuple__, __exec__
from lineapy.utils import get_new_id

logger = logging.getLogger(__name__)


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
        nodes = self.records_manager.db.get_nodes_for_session(
            self.session_context.id
        )
        return Graph(nodes, self.session_context)

    @property
    def values(self) -> dict[str, object]:
        return {k: n.value for k, n in self.variable_name_to_node.items()}

    @property
    def stdout(self) -> str:
        return self.executor.get_stdout()

    def slice(self, artifact_name: str) -> str:
        """
        Gets the code for a slice of the graph from an artifact
        """
        artifact = self.db.get_artifact_by_name(artifact_name)
        return get_program_slice(self.graph, [LineaID(cast(str, artifact.id))])

    def process_node(self, node: Node) -> None:
        """
        Execute a node, and adds it to the database.
        """
        self.executor.execute_node(node)
        self.records_manager.add_evaluated_nodes(node)

    def exit(self):
        nodes = self.records_manager.records_pool
        try:
            self.records_manager.exit()
        except Exception:
            logger.exception(
                "Error writing nodes %s", Graph(nodes, self.session_context)
            )
            raise

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
            self.process_node(new_node)
            return new_node

    # TODO: Refactor to take in node id
    def publish(
        self, variable_name: str, description: Optional[str] = None
    ) -> None:
        node_id = self.lookup_node(variable_name).id
        self.records_manager.add_node_id_to_artifact_table(
            node_id, description
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
        self.process_node(node)

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
        self.process_node(node)
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
        """
        node = CallNode(
            id=get_new_id(),
            session_id=self.session_context.id,
            function_id=function_node.id,
            positional_args=[n.id for n in arguments],
            keyword_args={k: n.id for k, n, in keyword_arguments.items()},
            source_location=source_location,
        )
        self.process_node(node)

        _resulting_spec = inspect_function(
            function_node.value,
            [n.value for n in arguments],
            {k: v.value for k, v in keyword_arguments.items()},
            node.value,
        )
        # TODO: Process spec and add mutations
        return node

    def assign(
        self,
        variable_name: str,
        value_node: Node,
    ) -> None:
        """
        Assign updates a local mapping of variable nodes.

        It doesn't save this to the graph, and currently the source
        location for the assignment is discarded. In the future, if we need
        to trace where in some code a node is assigned, we can record that again.
        """
        logger.info("assigning %s = %s", variable_name, value_node)
        self.variable_name_to_node[variable_name] = value_node
        return

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
