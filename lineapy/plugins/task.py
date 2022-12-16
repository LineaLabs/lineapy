from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import Dict, List, Set, Tuple

import networkx as nx

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
        mapping: Dict[str, str],
        edges: TaskGraphEdge = {},
    ):
        self.graph = nx.DiGraph()
        self.artifact_raw_to_safe_mapping = mapping
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

        nx.relabel_nodes(self.graph, mapping, copy=False)

    def get_taskorder(self) -> List[str]:
        return list(nx.topological_sort(self.graph))


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

    LocalPickle = 1
    # TODO: lineapy.get and lineapy.save


def extract_taskgraph(
    artifacts: List[str], dependencies: TaskGraphEdge
) -> Tuple[List[str], TaskGraph]:
    """
    extract_taskgraph returns a list of artifacts and the taskgraph corresponding to the provided dependencies
    """
    artifact_safe_names = []
    for artifact_name in artifacts:
        artifact_var = slugify(artifact_name)
        if len(artifact_var) == 0:
            raise ValueError(f"Invalid slice name {artifact_name}.")
        artifact_safe_names.append(artifact_var)

    task_graph = TaskGraph(
        artifacts,
        {slice: task for slice, task in zip(artifacts, artifact_safe_names)},
        dependencies,
    )
    return (artifact_safe_names, task_graph)


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
