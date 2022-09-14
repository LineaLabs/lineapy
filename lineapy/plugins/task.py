from enum import Enum
from itertools import chain
from typing import Dict, List, Optional, Set

import networkx as nx
from typing_extensions import TypedDict

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

    # Depreciate after new to_pipeline is implemented
    def get_airflow_dependency(self):
        return (
            "\n".join(
                [f"{task0}>> {task1}" for task0, task1 in self.graph.edges]
            )
            if len(list(self.graph.edges)) > 0
            else ""
        )

    def get_airflow_dependencies(
        self,
        setup_task: Optional[str] = None,
        teardown_task: Optional[str] = None,
    ):
        taskorder = [
            task for task in self.get_taskorder() if task in self.graph.nodes
        ]
        dependencies = [
            f"{task0}>> {task1}" for task0, task1 in self.graph.edges
        ]
        if setup_task is not None:
            dependencies.append(f"{setup_task} >> {taskorder[0]}")
        if teardown_task is not None:
            dependencies.append(f"{taskorder[-1]} >> {teardown_task}")
        return dependencies


class AirflowDagFlavor(Enum):
    PythonOperatorPerSession = 1
    PythonOperatorPerArtifact = 2
    # To be implemented for different flavor of airflow dags
    # BashOperator = 3
    # DockerOperator = 4
    # KubernetesPodOperator = 5


AirflowDagConfig = TypedDict(
    "AirflowDagConfig",
    {
        "owner": str,
        "retries": int,
        "start_date": str,
        "schedule_interval": str,
        "max_active_runs": int,
        "catchup": str,
        "dag_flavor": str,  # Not native to Airflow config
    },
    total=False,
)


class TaskDefinition(TypedDict):
    """
    Definition of an artifact, can extend new keys(user, project, ...)
    in the future.
    """

    definition: str
    user_input_variables: List[str]
