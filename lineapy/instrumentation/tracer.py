import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from itertools import chain
from os import getcwd
from typing import Dict, Optional

from black import FileMode, format_str

from lineapy.constants import GETATTR
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    GlobalNode,
    ImportNode,
    Library,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
    SessionContext,
    SessionType,
    SourceLocation,
)
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ArtifactORM
from lineapy.execution.executor import (
    ID,
    AccessedGlobals,
    Executor,
    ExecutorPointer,
    ImplicitDependencyNode,
    Variable,
    ViewOfNodes,
)
from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.instrumentation.mutation_tracker import MutationTracker
from lineapy.lineabuiltins import l_tuple
from lineapy.utils import get_new_id, remove_duplicates, remove_value

logger = logging.getLogger(__name__)


@dataclass
class Tracer:
    db: RelationalLineaDB

    session_type: InitVar[SessionType]
    session_name: InitVar[Optional[str]] = None
    globals_: InitVar[Optional[dict[str, object]]] = None

    variable_name_to_node: Dict[str, Node] = field(default_factory=dict)

    session_context: SessionContext = field(init=False)
    executor: Executor = field(init=False)
    mutation_tracker: MutationTracker = field(default_factory=MutationTracker)

    def __post_init__(
        self,
        session_type: SessionType,
        session_name: Optional[str],
        globals_: Optional[dict[str, object]],
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
        self.executor = Executor(self.db, globals_ or globals())
        self.session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name=session_name,
            execution_id=self.executor.execution.id,
        )
        self.db.write_context(self.session_context)

    @property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = self.db.get_nodes_for_session(self.session_context.id)
        return Graph(nodes, self.session_context)

    @property
    def values(self) -> dict[str, object]:
        """
        Returns a mapping of variable names to their values, by joining
        the scoping information with the executor values.
        """
        return {
            k: self.executor.get_value(n)
            for k, n in self.variable_name_to_node.items()
        }

    @property
    def artifacts(self) -> dict[str, str]:
        """
        Returns a mapping of artifact names to their sliced code.
        """

        return {
            artifact.name: get_program_slice(self.graph, [artifact.node_id])
            for artifact in self.session_artifacts()
            if artifact.name is not None
        }

    def sliced_func(self, slice_name: str, func_name: str) -> str:
        artifact = self.db.get_artifact_by_name(slice_name)
        artifact_var = self.slice_var_name(artifact)
        if not artifact_var:
            return "Unable to extract the slice"
        slice_code = get_program_slice(self.graph, [artifact.node_id])
        # We split the code in import and code blocks and join them to full code test
        import_block, code_block, main_block = split_code_blocks(
            slice_code, func_name
        )
        full_code = (
            import_block
            + "\n\n"
            + code_block
            + f"\n\treturn {artifact_var}"
            + "\n\n"
            + main_block
        )
        # Black lint
        black_mode = FileMode()
        black_mode.line_length = 79
        full_code = format_str(full_code, mode=black_mode)
        return full_code

    def session_artifacts(self) -> list[ArtifactORM]:
        return self.db.get_artifacts_for_session(self.session_context.id)

    def slice(self, name: str) -> str:
        artifact = self.db.get_artifact_by_name(name)
        return get_program_slice(self.graph, [artifact.node_id])

    def slice_var_name(self, artifact: ArtifactORM) -> str:
        """
        Returns the variable name for the given artifact.
        i.e. in lineapy.save(p, "p value") "p" is returned
        """
        if not artifact.node:
            return ""
        _line_no = artifact.node.lineno if artifact.node.lineno else 0
        artifact_line = str(artifact.node.source_code.code).split("\n")[
            _line_no - 1
        ]
        _col_offset = (
            artifact.node.col_offset if artifact.node.col_offset else 0
        )
        if _col_offset < 3:
            return ""
        return artifact_line[: _col_offset - 3]

    def process_node(self, node: Node) -> None:
        """
        Execute a node, and adds it to the database.
        """

        ##
        # Update the graph from the side effects of the node,
        ##
        side_effects = self.executor.execute_node(
            node, {k: v.id for k, v in self.variable_name_to_node.items()}
        )

        # Iterate through each side effect and process it, depending on its type
        for e in side_effects:
            if isinstance(e, ImplicitDependencyNode):
                self._process_implicit_dependency(
                    node, self._resolve_pointer(e.pointer)
                )
            elif isinstance(e, ViewOfNodes):
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

        self.db.write_node(node)

    def _resolve_pointer(self, ptr: ExecutorPointer) -> LineaID:
        if isinstance(ptr, ID):
            return ptr.id
        if isinstance(ptr, Variable):
            return self.variable_name_to_node[ptr.name].id
        # Handle external state case, by making a lookup node for it
        return self.lookup_node(ptr.__name__).id

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
            self.mutation_tracker.get_latest_mutate_node(implicit_dependency_id)
        )

    def _process_accessed_globals(
        self,
        session_id: str,
        node: Node,
        retrieved: list[str],
        added_or_updated: list[str],
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
        self.db.add_lib_to_session_context(self.session_context.id, library)
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
            positional_args=[
                self.mutation_tracker.get_latest_mutate_node(n.id)
                for n in arguments
            ],
            keyword_args={
                k: self.mutation_tracker.get_latest_mutate_node(n.id)
                for k, n, in keyword_arguments.items()
            },
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
