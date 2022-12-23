from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import Dict, List, Set, Tuple

import networkx as nx
from networkx.exception import NetworkXUnfeasible

from lineapy.plugins.utils import load_plugin_template, slugify

TaskGraphEdge = Dict[str, Set[str]]


class TaskGraph(object):
    """
    Graph represents for task dependency
    It is constructed based on the "edges" variable

    :param edges: Dictionary with task name as key and set of prerequisite 
        tasks as value. This is the standard library `graphlib` style graph 
        definition. For instance, {'C':{'A','B'}} means A and B are 
        prerequisites for C. Both examples give us following task dependency::

            A ---\\
                  \\
                   >---> C
                  /
            B ---/


    .. note::

        - If we only support Python 3.9+, we prefer to use graphlib in standard 
          library instead of networkx for graph operation.

        - We might want to get rid of the mapping for renaming slice_names to 
          task_names.

    """

    def __init__(
        self,
        nodes: List[str],
        edges: TaskGraphEdge = {},
    ):
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(nodes)
        # parsing the other format to our tuple-based format
        # note that nesting is not allowed (enforced by the type signature)
        # per the spec in https://docs.python.org/3/library/graphlib.html
        graph_edges = list(
            chain.from_iterable(
                ((node, to_node) for node in from_node)
                for to_node, from_node in edges.items()
            )
        )
        self.graph.add_edges_from(graph_edges)

    def copy(
        self,
    ) -> TaskGraph:
        copied_taskgraph = TaskGraph([])
        copied_taskgraph.graph = self.graph.copy()
        return copied_taskgraph

    def remap_nodes(self, mapping: Dict[str, str]) -> TaskGraph:
        remapped_taskgraph = TaskGraph([])
        remapped_taskgraph.graph = nx.relabel_nodes(
            self.graph, mapping, copy=True
        )
        return remapped_taskgraph

    def insert_setup_task(self, setup_task_name: str):
        """
        insert_setup_task adds a setup task that will be run before all the original source tasks
        """

        self.graph.add_node(setup_task_name)

        for old_source in self.source_nodes:
            if not old_source == setup_task_name:
                self.graph.add_edge(setup_task_name, old_source)

    def insert_teardown_task(self, cleanup_task_name: str):
        """
        insert_cleanup_task adds a cleanup task that will be run after all the original sink tasks
        """

        self.graph.add_node(cleanup_task_name)

        for old_sink in self.sink_nodes:
            if not old_sink == cleanup_task_name:
                self.graph.add_edge(old_sink, cleanup_task_name)

    def get_taskorder(self) -> List[str]:
        try:
            return list(nx.topological_sort(self.graph))
        except NetworkXUnfeasible:
            raise Exception(
                "Current implementation of LineaPy demands it be able to linearly order different sessions, "
                "which prohibits any circular dependencies between sessions. "
                "Please check if your provided dependencies include such circular dependencies between sessions, "
                "e.g., Artifact A (Session 1) -> Artifact B (Session 2) -> Artifact C (Session 1)."
            )

    def remove_self_loops(self):
        self.graph.remove_edges_from(nx.selfloop_edges(self.graph))

    @property
    def sink_nodes(self):
        return [
            node
            for node in self.graph.nodes
            if self.graph.out_degree(node) == 0
        ]

    @property
    def source_nodes(self):
        return [
            node
            for node in self.graph.nodes
            if self.graph.in_degree(node) == 0
        ]


def slugify_dependencies(dependencies: TaskGraphEdge) -> TaskGraphEdge:
    # slugify dependencies and save to self.dependencies
    slugified_dependencies: TaskGraphEdge = {}
    for to_artname, from_artname_set in dependencies.items():
        slugified_dependencies[slugify(to_artname)] = set()
        for from_artname in from_artname_set:
            slugified_dependencies[slugify(to_artname)].add(
                slugify(from_artname)
            )

    return slugified_dependencies


@dataclass
class TaskDefinition:
    """
    Definition of an artifact, can extend new keys(user, project, ...)
    in the future.

        function_name: suggested function name this task that wont conflict with other linea generated tasks
        user_input_variables: arguments that must be provided through the framework
        loaded_input_variables: arguments that are provided by other tasks and must be loaded through inter task communication
        typing_blocks: for user_input_variables, casts the input variables to the correct type
        call_block: line of code to call the function in module file
        return_vars: outputs that need to be serialized to be used
        pipeline_name: overall pipeline name

    """

    function_name: str
    user_input_variables: List[str]
    loaded_input_variables: List[str]
    typing_blocks: List[str]
    pre_call_block: str
    call_block: str
    post_call_block: str
    return_vars: List[str]
    pipeline_name: str


class DagTaskBreakdown(Enum):
    """
    Enum to define how to break down a graph into tasks for the pipeline.
    """

    TaskAllSessions = 1  # all sessions are one task
    TaskPerSession = 2  # each session corresponds to one task
    TaskPerArtifact = 3  # each artifact or common variable is a task


class TaskSerializer(Enum):
    """Enum to define what type of object serialization to use for inter task communication."""

    # Write to local pickle directory under /tmp/
    LocalPickle = 1
    # Write to a pickle directory that can be parametrized
    ParametrizedPickle = 2
    # TODO: lineapy.get and lineapy.save


def render_task_io_serialize_blocks(
    taskdef: TaskDefinition, task_serialization: TaskSerializer
) -> Tuple[List[str], List[str]]:
    """
    render_task_io_serialize_blocks renders object ser and deser code blocks.

    These code blocks can be used for inter task communication.
    This function returns the task deserialization block first,
    since this block should be included first in the function to load the variables.
    """
    task_serialization_blocks = []
    task_deserialization_block = []

    if task_serialization == TaskSerializer.LocalPickle:
        SERIALIZER_TEMPLATE = load_plugin_template(
            "task/localpickle/task_local_pickle_ser.jinja"
        )
        DESERIALIZER_TEMPLATE = load_plugin_template(
            "task/localpickle/task_local_pickle_deser.jinja"
        )
    elif task_serialization == TaskSerializer.ParametrizedPickle:
        SERIALIZER_TEMPLATE = load_plugin_template(
            "task/parameterizedpickle/task_parameterized_ser.jinja"
        )
        DESERIALIZER_TEMPLATE = load_plugin_template(
            "task/parameterizedpickle/task_parameterized_deser.jinja"
        )
    # Add more renderable task serializers here

    for loaded_input_variable in taskdef.loaded_input_variables:
        task_deserialization_block.append(
            DESERIALIZER_TEMPLATE.render(
                loaded_input_variable=loaded_input_variable,
                pipeline_name=taskdef.pipeline_name,
            )
        )
    for return_variable in taskdef.return_vars:
        task_serialization_blocks.append(
            SERIALIZER_TEMPLATE.render(
                return_variable=return_variable,
                pipeline_name=taskdef.pipeline_name,
            )
        )

    return task_deserialization_block, task_serialization_blocks
