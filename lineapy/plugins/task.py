from itertools import chain
from typing import Dict, List, Set

import networkx as nx

TaskGraphEdge = Dict[str, Set[str]]


class TaskGraph(object):
    """
    Graph represents for task dependency
    It is constructed based on the following variables:
    :param edges: Dictionary with task name as key and set of prerequisite 
        tasks as value. This is the standard library `graphlib` style graph 
        definition. For instance, {'C':{'A','B'}} means A and B are 
        prerequisites for C. Both examples give us following task dependency
        A ---\
              \
               >---> C
              /
        B ---/

    NOTE:
    - If we only support Python 3.9+, we prefer to use grathlib in standard 
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

    def get_airflow_dependency(self):
        return (
            "\n".join(
                [f"{task0}>> {task1}" for task0, task1 in self.graph.edges]
            )
            if len(list(self.graph.edges)) > 0
            else ""
        )
