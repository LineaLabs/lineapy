import itertools
import string
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Set

import networkx as nx

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)


@dataclass
class GraphSegment:
    graph_segment: Graph
    dependent_variables: Set[str]
    created_variables: Set[str]
    related_variables: Set[str]
    required_variables: Set[str]
    return_variables: Set[str]


@dataclass
class GraphRefactorer:
    """
    Refactor a given session graph for use in a downstream task (e.g., pipeline building).
    """

    db: RelationalLineaDB

    def _segment_session_graph_by_artifacts(self, session_id) -> str:
        # Map each variable node ID to the corresponding variable name
        session_variables = self.db.get_variables_for_session(session_id)
        variable_dict = defaultdict(set)
        for node_id, variable_name in session_variables:
            variable_dict[node_id].add(variable_name)

        # Map each artifact node ID to the corresponding artifact name
        session_artifacts = self.db.get_artifacts_for_session(session_id)
        artifact_dict = {
            artifact.node_id: artifact.name for artifact in session_artifacts
        }

        # Get the full session graph
        session_context = self.db.get_session_context(session_id)
        nodes = self.db.get_nodes_for_session(session_id)
        full_graph = Graph(nodes, session_context)
        full_nxgraph = full_graph.nx_graph

        # Identify variable dependencies of each node in topological order
        node_dependency = dict()
        for node_id in nx.topological_sort(full_nxgraph):
            predecessors = full_nxgraph.predecessors(node_id)
            node_dependency[node_id] = set()
            for p_node_id in predecessors:
                dep = variable_dict.get(p_node_id, node_dependency[p_node_id])
                node_dependency[node_id] = node_dependency[node_id].union(dep)

        # Identify artifact nodes and topologically sort them
        artifact_ids_sorted = [
            node_id
            for node_id in nx.topological_sort(full_nxgraph)
            if node_id in artifact_dict
        ]

        # Construct a collection of graph segments
        used_node_ids = set()  # Track nodes that get ever used
        art_segment_dict = OrderedDict()
        for art_id in artifact_ids_sorted:
            # Identify "non-overlapping" nodes that solely belong to the artifact
            art_name = artifact_dict[art_id]
            art_slice = get_slice_graph(full_graph, [art_id])
            art_node_ids = set(art_slice.nx_graph.nodes) - used_node_ids
            art_graph_segment = full_graph.get_subgraph(
                [full_graph.get_node(node_id) for node_id in art_node_ids]
            )

            # Update used nodes for next iteration
            used_node_ids = used_node_ids.union(art_node_ids)

            # Calculate the artifact's variable relations
            dependent_variables = set(
                itertools.chain.from_iterable(
                    [node_dependency[node_id] for node_id in art_node_ids]
                )
            )
            created_variables = set(
                itertools.chain.from_iterable(
                    [
                        variable_dict.get(node_id, set())
                        for node_id in art_node_ids
                    ]
                )
            )
            related_variables = dependent_variables.union(created_variables)
            required_variables = related_variables - created_variables
            return_variables = set([art_name])  # FIXME: Should be var name

            # Create graph segment object for the artifact
            art_segment_dict[art_name] = GraphSegment(
                graph_segment=art_graph_segment,
                dependent_variables=dependent_variables,
                created_variables=created_variables,
                related_variables=related_variables,
                required_variables=required_variables,
                return_variables=return_variables,
            )

        # Update `return_variables`` in each artifact segment to account for downstream requirements
        for i, art_segment in enumerate(art_segment_dict.values()):
            for p, prev_art_segment in enumerate(art_segment_dict.values()):
                if p < i:
                    variables_required_downstream = (
                        prev_art_segment.related_variables.intersection(
                            art_segment.required_variables
                        )
                    )
                    prev_art_segment.return_variables = (
                        prev_art_segment.return_variables.union(
                            variables_required_downstream
                        )
                    )

        return art_segment_dict
