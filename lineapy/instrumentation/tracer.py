import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from os import getcwd
from typing import Dict, List, Optional, Tuple, Union

from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    GlobalNode,
    ImportNode,
    KeywordArgument,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
    PositionalArgument,
    SessionContext,
    SessionType,
    SourceLocation,
)
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.execution.executor import Executor
from lineapy.execution.side_effects import (
    ID,
    AccessedGlobals,
    ExecutorPointer,
    ImplicitDependencyNode,
    Variable,
    ViewOfNodes,
)
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.instrumentation.tracer_context import TracerContext
from lineapy.utils.constants import GETATTR, IMPORT_STAR
from lineapy.utils.lineabuiltins import l_tuple
from lineapy.utils.utils import get_lib_package_version, get_new_id

logger = logging.getLogger(__name__)


@dataclass
class Tracer:
    db: RelationalLineaDB

    session_type: InitVar[SessionType]
    session_name: InitVar[Optional[str]] = None
    globals_: InitVar[Optional[Dict[str, object]]] = None

    variable_name_to_node: Dict[str, Node] = field(default_factory=dict)

    tracer_context: TracerContext = field(init=False)
    executor: Executor = field(init=False)
    mutation_tracker: MutationTracker = field(default_factory=MutationTracker)

    def __post_init__(
        self,
        session_type: SessionType,
        session_name: Optional[str],
        globals_: Optional[Dict[str, object]],
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

        Note that we don't currently maintain the variable names in the persisted
        graph (we used to at some point in the past), but we can add a serialized
        version of `variable_name_to_id` to the session if we want to persist
        the information. Which could be useful for e.g., post-hoc lifting of
        linea artifacts.
        """
        self.executor = Executor(self.db, globals_ or globals())

        session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name=session_name,
            execution_id=self.executor.execution.id,
        )
        self.db.write_context(session_context)
        self.tracer_context = TracerContext(
            session_context=session_context, db=self.db
        )

    @property
    def values(self) -> Dict[str, object]:
        """
        Returns a mapping of variable names to their values, by joining
        the scoping information with the executor values.
        """
        return {
            k: self.executor.get_value(n.id)
            for k, n in self.variable_name_to_node.items()
        }

    def process_node(self, node: Node) -> None:
        """
        Execute a node, and adds it to the database.
        """

        ##
        # Update the graph from the side effects of the node,
        # If an artifact could not be created, quitely return without saving
        # the node to the DB.
        ##
        logger.debug("Executing node %s", node)
        try:
            side_effects = self.executor.execute_node(
                node,
                {k: v.id for k, v in self.variable_name_to_node.items()},
            )
        except ArtifactSaveException as exc_info:
            logger.error("Artifact could not be saved.")
            logger.debug(exc_info)
            return
        logger.debug("Processing side effects")

        # Iterate through each side effect and process it, depending on its type
        for e in side_effects:
            if isinstance(e, ImplicitDependencyNode):
                self._process_implicit_dependency(
                    node, self._resolve_pointer(e.pointer)
                )
            elif isinstance(e, ViewOfNodes):
                if len(e.pointers) > 0:  # skip if empty
                    self.mutation_tracker.set_as_viewers_of_eachother(
                        *map(self._resolve_pointer, e.pointers)
                    )
            elif isinstance(e, AccessedGlobals):
                self._process_accessed_globals(
                    node.session_id, node, e.retrieved, e.added_or_updated
                )
            # Mutate case
            else:
                mutated_node_id = self._resolve_pointer(e.pointer)
                for (
                    mutate_node_id,
                    source_id,
                ) in self.mutation_tracker.set_as_mutated(mutated_node_id):
                    mutate_node = MutateNode(
                        id=mutate_node_id,
                        session_id=node.session_id,
                        source_id=source_id,
                        call_id=node.id,
                    )
                    self.process_node(mutate_node)

        # also special case for import node
        if isinstance(node, ImportNode):
            # must process after the call has been executed
            package_name, version = get_lib_package_version(node.name)
            node.version = version
            node.package_name = package_name

        self.db.write_node(node)

    def _resolve_pointer(self, ptr: ExecutorPointer) -> LineaID:
        if isinstance(ptr, ID):
            return ptr.id
        if isinstance(ptr, Variable):
            return self.variable_name_to_node[ptr.name].id
        # Handle external state case, by making a lookup node for it
        if isinstance(ptr, ExternalState):
            return (
                self.executor.lookup_external_state(ptr)
                or self.lookup_node(ptr.external_state).id
            )
        raise ValueError(f"Unsupported pointer type: {type(ptr)}")

    def _process_implicit_dependency(
        self, node: Node, implicit_dependency_id: LineaID
    ) -> None:
        """
        Add dependency of a node on a global implicit dependency,
        which is a dependency that lineapy has deemed essential in the
        reproduction of an artifact but is not explicitly passed as arguments
        """

        # Only call nodes can refer to implicit dependencies
        assert isinstance(node, CallNode)
        node.implicit_dependencies.append(
            self.mutation_tracker.get_latest_mutate_node(
                implicit_dependency_id
            )
        )

    def _process_accessed_globals(
        self,
        session_id: str,
        node: Node,
        retrieved: List[str],
        added_or_updated: List[str],
    ) -> None:

        # Only call nodes can access globals and have the global_reads attribute
        assert isinstance(node, CallNode)

        # Add the retrieved globals as global reads to the call node
        node.global_reads = {
            var: self.mutation_tracker.get_latest_mutate_node(
                self.variable_name_to_node[var].id
            )
            for var in retrieved
            # Only save reads from variables that we have already saved variables for
            # Assume that all other reads are for variables assigned inside the call
            if var in self.variable_name_to_node
        }

        # Create a new global node for each added/updated
        for var in added_or_updated:
            global_node = GlobalNode(
                id=get_new_id(),
                session_id=session_id,
                name=var,
                call_id=node.id,
            )
            self.process_node(global_node)
            self.variable_name_to_node[var] = global_node

    def lookup_node(
        self,
        variable_name: str,
        source_location: Optional[SourceLocation] = None,
    ) -> Node:
        """
        Cases for the node that we are looking up:

        - user defined variable & function definitions
        - imported libs
        - unknown runtime magic functions---special case to LookupNode

          - builtin functions, e.g., min
          - custom runtime, e.g., get_ipython

        """
        if variable_name in self.variable_name_to_node:
            # user define var and fun def
            return self.variable_name_to_node[variable_name]
        else:
            new_node = LookupNode(
                id=get_new_id(),
                session_id=self.get_session_id(),
                name=variable_name,
                source_location=source_location,
            )
            self.process_node(new_node)
            return new_node

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
        ----
        - The input args would _either_ have alias or attributes, but not both
        - Didn't call the function import because I think that's a protected name

        note that version and path will be introspected at runtime
        """
        node = ImportNode(
            id=get_new_id(),
            name=name,
            session_id=self.get_session_id(),
            source_location=source_location,
        )
        self.process_node(node)

        if attributes is None:
            self.variable_name_to_node[alias or name] = node

        # for the attributes imported, we need to add them to the local lookup
        #  that yields the importnode's id for the `function_module` field,
        #  see `graph_with_basic_image`.

        else:
            if IMPORT_STAR in attributes:
                module_value = self.executor.get_value(node.id)
                # Import star behavior copied from python docs
                # https://docs.python.org/3/reference/simple_stmts.html#the-import-statement
                if hasattr(module_value, "__all__"):
                    public_names = module_value.__all__  # type: ignore
                else:
                    public_names = [
                        attr
                        for attr in dir(module_value)
                        if not attr.startswith("_")
                    ]
                attributes = {attr: attr for attr in public_names}
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

        return

    def literal(
        self,
        value: object,
        source_location: Optional[SourceLocation] = None,
    ):
        # this literal should be assigned or used later
        node = LiteralNode(
            id=get_new_id(),
            session_id=self.get_session_id(),
            value=value,
            source_location=source_location,
        )
        self.process_node(node)
        return node

    def __get_positional_arguments(self, arguments):
        for arg in arguments:
            if isinstance(arg, tuple) or isinstance(arg, list):
                yield PositionalArgument(
                    id=self.mutation_tracker.get_latest_mutate_node(arg[1].id),
                    starred=arg[0],
                )

            else:
                yield PositionalArgument(
                    id=self.mutation_tracker.get_latest_mutate_node(arg.id),
                    starred=False,
                )

    def __get_keyword_arguments(self, keyword_arguments):
        for k, n in keyword_arguments.items():
            values = self.mutation_tracker.get_latest_mutate_node(n.id)
            if k.startswith("unpack_"):
                yield KeywordArgument(key="**", value=values, starred=True)
            else:
                yield KeywordArgument(key=k, value=values, starred=False)

    def call(
        self,
        function_node: Node,
        source_location: Optional[SourceLocation],
        # function_name: str,
        *arguments: Union[Node, Tuple[bool, Node]],
        **keyword_arguments: Node,
    ) -> CallNode:
        """
        :param function_node: the function node to call/execute
        :param source_location: the source info from user code
        :param arguments: positional arguments. These are passed as either Nodes (named nodes, constants, etc)
                        or tuples (starred, the node) where the starred is a boolean to indicate whether
                            the argument is supposed to be splatted before passing to the function (This is
                            the case where you might call a function like so ``foo(1, *[2, 3])`` ). The boolean is made
                            optional simply to support the legacy way of calling this function and not having to pass
                            the tuples for every single case from node_transformer
        :param keyword_arguments: keyword arguments. These are passed as a dictionary of keyword arguments to the
                                    function. Similar to ``*positional_arguments``, the keyword arguments can also be splatted
                                    by naming the key as ``unpack_<index>`` where <index> is the index of the argument. In this
                                    case, the dictionary will be unpacked and passed as keyword arguments to the function.
                                    The keyword arguments are processed in order of passing so any keyword conflicts will
                                    result in the last value accepted as the value for the keyword.
        :return: a call node

        NOTE
        ----
        - It's important for the call to return the call node
          so that we can programmatically chain the the nodes together,
          e.g., for the assignment call to modify the previous call node.
        - The call looks up if it's a locally defined function. We decided
          that this is better for program slicing.
        """

        node = CallNode(
            id=get_new_id(),
            session_id=self.get_session_id(),
            function_id=function_node.id,
            positional_args=self.__get_positional_arguments(arguments),
            keyword_args=self.__get_keyword_arguments(keyword_arguments),
            source_location=source_location,
            global_reads={},
            implicit_dependencies=[],
        )
        self.process_node(node)
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
        logger.debug("assigning %s = %s", variable_name, value_node)
        self.variable_name_to_node[variable_name] = value_node
        return

    def tuple(
        self, *args: Node, source_location: Optional[SourceLocation] = None
    ) -> CallNode:
        return self.call(
            self.lookup_node(l_tuple.__name__),
            source_location,
            *args,
        )

    # tracer context method wrappers from here on
    def get_session_id(self) -> LineaID:
        return self.tracer_context.get_session_id()

    @property
    def graph(self) -> Graph:
        return self.tracer_context.graph

    def session_artifacts(self) -> List[ArtifactORM]:
        return self.tracer_context.session_artifacts()

    @property
    def artifacts(self) -> Dict[str, str]:
        return self.tracer_context.artifacts

    def slice(self, name: str) -> str:
        return self.tracer_context.slice(name)

    def get_working_dir(self) -> str:
        return self.tracer_context.session_context.working_directory
