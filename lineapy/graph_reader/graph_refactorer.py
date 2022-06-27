import itertools
import string
from collections import defaultdict
from dataclasses import dataclass

import networkx as nx

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)


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
        for node_id in nx.topological_sort(full_graph.nx_graph):
            predecessors = full_nxgraph.predecessors(node_id)
            node_dependency[node_id] = set()
            for p_node_id in predecessors:
                dep = variable_dict.get(p_node_id, node_dependency[p_node_id])
                node_dependency[node_id] = node_dependency[node_id].union(dep)

        # Identify artifact nodes and topologically sort them
        artifact_ordering = [
            (artifact_dict[node_id], node_id)
            for node_id in nx.topological_sort(full_nxgraph)
            if artifact_dict.get(node_id) is not None
        ]

        used_nodes = set()  # Track nodes that get ever used
        nonoverlapping_artifact_graph = {}
        artifact_variables = {}
        for art_name, art_id in artifact_ordering:
            artifact_subgraph = get_slice_graph(full_graph, [art_id])
            artifact_nodes = set(artifact_subgraph.nx_graph.nodes) - used_nodes

            nonoverlapping_artifact_graph[art_name] = full_graph.get_subgraph(
                [
                    full_graph.get_node(node_id)
                    for node_id in set(artifact_nodes) - used_nodes
                ]
            )
            used_nodes = used_nodes.union(
                set(nonoverlapping_artifact_graph[art_name].nx_graph.nodes)
            )
            dependent_variables = set(
                itertools.chain.from_iterable(
                    [node_dependency[node_id] for node_id in artifact_nodes]
                )
            )
            created_variables = set(
                itertools.chain.from_iterable(
                    [
                        variable_dict.get(node_id, set())
                        for node_id in artifact_nodes
                    ]
                )
            )
            related_variables = dependent_variables.union(created_variables)
            required_variables = related_variables - created_variables
            return_variables = set([art_name])

            artifact_variables[art_name] = {
                "dependent_variables": dependent_variables,
                "created_variables": created_variables,
                "related_variables": related_variables,
                "required_variables": required_variables,
                "return_variables": return_variables,
            }

        for i, (art_name, _) in enumerate(artifact_ordering):
            required_variable = artifact_variables[art_name][
                "required_variables"
            ]
            for p, (prev_art_name, _) in enumerate(artifact_ordering):
                if p < i:
                    artifact_variables[prev_art_name][
                        "return_variables"
                    ] = artifact_variables[prev_art_name][
                        "return_variables"
                    ].union(
                        artifact_variables[prev_art_name][
                            "related_variables"
                        ].intersection(required_variable)
                    )

        return artifact_variables
