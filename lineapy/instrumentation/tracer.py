import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

from lineapy.data.types import (
    CallNode,
    GlobalNode,
    ImportNode,
    KeywordArgument,
    Library,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
    PositionalArgument,
    SessionContext,
    SourceLocation,
)
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.execution.executor import (
    ID,
    AccessedGlobals,
    ExecutorPointer,
    ImplicitDependencyNode,
    Variable,
    ViewOfNodes,
)
from lineapy.global_context import GlobalContext
from lineapy.instrumentation.annotation_spec import ExternalState
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.operator import BaseOperator
from lineapy.utils.constants import GETATTR, IMPORT_STAR
from lineapy.utils.lineabuiltins import l_tuple
from lineapy.utils.utils import get_new_id

logger = logging.getLogger(__name__)


class Tracer(BaseOperator):
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

    # session_context: SessionContext = field(init=False)
    mutation_tracker: MutationTracker = MutationTracker()

    def __init__(self, context_manager: GlobalContext) -> None:
        self.context_manager = context_manager

    # TODO migrate to lgcontext
    def process_node(self, node: Node) -> None:
        """
        Execute a node, and adds it to the database.
        """

        ##
        # Update the graph from the side effects of the node,
        # If an artifact could not be created, quitely return without saving the node to the DB.
        ##
        try:
            # TODO - fix this by moving to notify function and handling in the context manager
            side_effects = self.context_manager.executor.execute_node(  # type: ignore
                node,
                {
                    k: v.id
                    for k, v in self.context_manager.variable_name_to_node.items()
                },
            )
        except ArtifactSaveException as exc_info:
            logger.error("Artifact could not be saved.")
            logger.debug(exc_info)
            return

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

        self.context_manager.db.write_node(node)

    def _resolve_pointer(self, ptr: ExecutorPointer) -> LineaID:
        if isinstance(ptr, ID):
            return ptr.id
        if isinstance(ptr, Variable):
            return self.context_manager.variable_name_to_node[ptr.name].id
        # Handle external state case, by making a lookup node for it
        if isinstance(ptr, ExternalState):
            return self.lookup_node(ptr.external_state).id
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
                self.context_manager.variable_name_to_node[var].id
            )
            for var in retrieved
            # Only save reads from variables that we have already saved variables for
            # Assume that all other reads are for variables assigned inside the call
            if var in self.context_manager.variable_name_to_node
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
            self.context_manager.variable_name_to_node[var] = global_node

    # TODO migrate to lgcontext
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
        if variable_name in self.context_manager.variable_name_to_node:
            # user define var and fun def
            return self.context_manager.variable_name_to_node[variable_name]
        else:
            new_node = LookupNode(
                id=get_new_id(),
                session_id=self.context_manager.session_context.id,
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
        library = Library(id=get_new_id(), name=name)
        node = ImportNode(
            id=get_new_id(),
            session_id=self.context_manager.session_context.id,
            library=library,
            source_location=source_location,
        )
        self.process_node(node)

        if attributes is None:
            if alias is not None:
                self.context_manager.variable_name_to_node[alias] = node
            else:
                self.context_manager.variable_name_to_node[name] = node

        # for the attributes imported, we need to add them to the local lookup
        #  that yields the importnode's id for the `function_module` field,
        #  see `graph_with_basic_image`.

        else:
            if IMPORT_STAR in attributes:
                module_value = self.context_manager.get_value(node.id)
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

        # also need to modify the session_context because of weird executor
        #   requirement; should prob refactor later
        # and we cannot just modify the runtime value because
        #   it's already written to disk
        self.context_manager.db.add_lib_to_session_context(
            self.context_manager.session_context.id, library
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
            session_id=self.context_manager.session_context.id,
            value=value,
            source_location=source_location,
        )
        self.process_node(node)
        return node

    def __get_positional_arguments(self, arguments):
        for arg in arguments:
            if isinstance(arg, tuple):
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
            session_id=self.context_manager.session_context.id,
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
        self.context_manager.variable_name_to_node[variable_name] = value_node
        return

    def tuple(
        self, *args: Node, source_location: Optional[SourceLocation] = None
    ) -> CallNode:
        return self.call(
            self.lookup_node(l_tuple.__name__),
            source_location,
            *args,
        )
