from itertools import chain, product
from typing import Dict, List, Set, Tuple, Union

import networkx as nx

TaskGraphEdge = Union[
    List[Tuple[Union[Tuple, str], Union[Tuple, str]]],
    Dict[str, Set[str]],
]


class TaskGraph(object):
    """
    Graph represents for task dependency
    It is constructed based on the following variables:
    :param edges: two options to define the edgelist to define the task graph
        1. List of tuples, each tuple has two elements. The first element is 
        the (tuple of) prerequisite task, and the second element is the (tuple
        of) task. For instance, [(('A','B'),'C')] means in order to run C, 
        both A and B need to be executed and the order of A and B does not
        matter.
        2. Dictionary with task name as key and set of prerequisite tasks as
        value. This is the standard library `graphlib` style graph definition.
        For instance, {'C':{'A','B'}} means A and B are prerequisites for C.
        Both examples give us following task dependency
        A ---\
              \
               >---> C
              /
        B ---/

    NOTE:
    - The edgelist you used in https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.add_edges_from.html should be compatible here.
    - If we only support Python 3.9+, we prefer to use grathlib in standard 
        library instead of networkx for graph operation.
    - We might want to get rid of the mapping for renaming slice_names to 
        task_names.
    """

    def __init__(
        self,
        nodes: List[str],
        mapping: Dict[str, str],
        edges: TaskGraphEdge = [],
    ):
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(nodes)
        if isinstance(edges, List):
            for i, (n0s, n1s) in enumerate(edges):
                if isinstance(n0s, str):
                    n0s = (n0s,)
                if isinstance(n1s, str):
                    n1s = (n1s,)
                self.graph.add_edges_from(product(n0s, n1s))
        else:
            edges = list(
                chain.from_iterable(
                    ((node, to_node) for node in from_node)
                    for to_node, from_node in edges.items()
                )
            )
            self.graph.add_edges_from(edges)

        nx.relabel_nodes(self.graph, mapping, copy=False)

    def get_edgelist(self) -> List[Tuple]:
        return list(self.graph.edges)

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
