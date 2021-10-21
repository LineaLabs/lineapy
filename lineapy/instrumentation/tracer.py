import logging
from collections import defaultdict
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from functools import cached_property
from os import getcwd
from typing import Dict, Literal, Optional, overload

from black import FileMode, format_str

from lineapy.constants import GET_ITEM, GETATTR
from lineapy.data.graph import Graph
from lineapy.data.types import (
    Artifact,
    CallNode,
    ImportNode,
    Library,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
    Node,
    NodeValue,
    SessionContext,
    SessionType,
    SourceLocation,
)
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.db.relational.schema.relational import ArtifactORM
from lineapy.execution.executor import Executor
from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.lineabuiltins import __build_tuple__, __exec__
from lineapy.utils import get_new_id, get_value_type
from lineapy.visualizer.graphviz import tracer_to_graphviz
from lineapy.visualizer.visual_graph import VisualGraphOptions

logger = logging.getLogger(__name__)


@dataclass
class Tracer:
    db: RelationalLineaDB

    session_type: InitVar[SessionType]
    session_name: InitVar[Optional[str]] = None

    variable_name_to_node: Dict[str, Node] = field(default_factory=dict)

    # Mapping of mutated nodes, from their original node id, to the latest
    # mutate node id they are the source of
    source_to_mutate: dict[LineaID, LineaID] = field(default_factory=dict)

    # Mapping of each node, to every node that has a "view" of it,
    # meaning that if that node is mutated, the view node will be as well
    source_to_viewers: dict[LineaID, set[LineaID]] = field(
        default_factory=lambda: defaultdict(set)
    )

    # Reverse mapping of node to viewers
    viewer_to_sources: dict[LineaID, set[LineaID]] = field(
        default_factory=lambda: defaultdict(set)
    )

    # Mapping from a node ID, which is the function node in a call node,
    # to a list of global variables that need to be set before it is called
    function_node_id_to_global_reads: dict[LineaID, list[str]] = field(
        default_factory=lambda: defaultdict(list)
    )

    session_context: SessionContext = field(init=False)
    executor: Executor = field(init=False)

    def __post_init__(
        self, session_type: SessionType, session_name: Optional[str]
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
        self.executor = Executor(self.db)
        self.session_context = SessionContext(
            id=get_new_id(),
            environment_type=session_type,
            creation_time=datetime.now(),
            working_directory=getcwd(),
            session_name=session_name,
            execution_id=self.executor.execution.id,
        )
        self.db.write_context(self.session_context)

    @cached_property
    def graph(self) -> Graph:
        """
        Creates a graph by fetching all the nodes about this session from the DB.
        """
        nodes = self.db.get_nodes_for_session(self.session_context.id)
        return Graph(nodes, self.session_context)

    @cached_property
    def values(self) -> dict[str, object]:
        """
        Returns a mapping of variable names to their values, by joining
        the scoping information with the executor values.
        """
        return {
            k: self.executor.get_value(n)
            for k, n in self.variable_name_to_node.items()
        }

    @cached_property
    def artifacts(self) -> dict[str, str]:
        """
        Returns a mapping of artifact names to their sliced code.
        """

        return {
            artifact.name: get_program_slice(self.graph, [artifact.id])
            for artifact in self.session_artifacts()
            if artifact.name is not None
        }

    def sliced_func(self, slice_name: str, func_name: str) -> str:
        artifact = self.db.get_artifact_by_name(slice_name)
        if not artifact.node:
            return "Unable to extract the slice"
        _line_no = artifact.node.lineno if artifact.node.lineno else 0
        artifact_line = str(artifact.node.source_code.code).split("\n")[
            _line_no - 1
        ]
        _col_offset = (
            artifact.node.col_offset if artifact.node.col_offset else 0
        )
        if _col_offset < 3:
            return "Unable to extract the slice"
        artifact_name = artifact_line[: _col_offset - 3]
        slice_code = get_program_slice(self.graph, [artifact.id])
        # We split the code in import and code blocks and join them to full code test
        import_block, code_block, main_block = split_code_blocks(
            slice_code, func_name
        )
        full_code = (
            import_block
            + "\n\n"
            + code_block
            + f"\n\treturn {artifact_name}"
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
        return get_program_slice(self.graph, [artifact.id])

    def visualize(
        self,
        filename="tracer",
        options: VisualGraphOptions = VisualGraphOptions(),
    ) -> None:
        """
        Visualize the graph using GraphViz, writing to disk and trying to open.
        """
        dot = tracer_to_graphviz(self, options)
        dot.render(filename, view=True, format="pdf")

    @property
    def stdout(self) -> str:
        return self.executor.get_stdout()

    def process_node(self, node: Node) -> None:
        """
        Execute a node, and adds it to the database.
        """
        self.db.write_node(node)

        side_effects = self.executor.execute_node(node)

        # Update the graph from the side effects of the node,
        # Creating additional views and mutate nodes

        # The viewer mappings are transitive closures, so whenever we add
        # a new view -> src, we have to traverse all of its parents and children
        # and add them as well.

        # Instead, we could have done the traversal when looking up the mutation
        for source_id, view_id in side_effects.views:
            self.source_to_viewers[source_id].add(view_id)
            self.viewer_to_sources[view_id].add(source_id)

            for parent_source in self.viewer_to_sources[source_id]:
                self.source_to_viewers[parent_source].add(view_id)
                self.viewer_to_sources[view_id].add(parent_source)

            for child_viewer in self.source_to_viewers[view_id]:
                self.source_to_viewers[source_id].add(child_viewer)
                self.viewer_to_sources[child_viewer].add(source_id)

        for original_source_id in side_effects.mutated:
            # Create a mutation node for every node that was mutated,
            # Which are all the views + the node itself
            for source_id in self.source_to_viewers[original_source_id] | {
                original_source_id
            }:
                mutate_node = MutateNode(
                    id=get_new_id(),
                    session_id=node.session_id,
                    source_id=self.resolve_node(source_id),
                    call_id=node.id,
                )
                self.source_to_mutate[source_id] = mutate_node.id
                self.process_node(mutate_node)

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

    def resolve_node(self, node_id: LineaID) -> LineaID:
        """
        Resolve a node to find the latest mutate node, that refers to it.

        Call this before creating a object based on another node.
        """
        # Keep looking up to see if their is a new mutated version of this
        # node
        while node_id in self.source_to_mutate:
            node_id = self.source_to_mutate[node_id]
        return node_id

    def publish(self, node: Node, description: Optional[str]) -> None:
        self.db.write_artifact(
            Artifact(
                id=self.resolve_node(node.id),
                date_created=datetime.now(),
                name=description,
            )
        )
        # serialize to db
        res = self.executor.get_value(node)
        timing = self.executor.get_execution_time(node.id)
        self.db.write_node_value(
            NodeValue(
                node_id=node.id,
                value=res,
                execution_id=self.executor.execution.id,
                start_time=timing[0],
                end_time=timing[1],
                value_type=get_value_type(res),
            )
        )
        # we have to commit eagerly because if we just add it
        #   to the queue, the `res` value may have mutated
        #   and that's incorrect.
        self.db.commit()

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
            positional_args=[self.resolve_node(n.id) for n in arguments],
            keyword_args={
                k: self.resolve_node(n.id)
                for k, n, in keyword_arguments.items()
            },
            source_location=source_location,
            global_reads={
                name: self.variable_name_to_node[name].id
                for name in sorted(
                    self.function_node_id_to_global_reads[function_node.id]
                )
            },
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
