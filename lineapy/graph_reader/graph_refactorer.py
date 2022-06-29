import itertools
import logging
import string
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple, Union

import networkx as nx

from lineapy.api.api import get
from lineapy.api.api_classes import LineaArtifact
from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


function_definition_template = string.Template(
    """def get_${aname}(${args_string}):
${artifact_codeblock}
${indentation_block}return ${return_string}
"""
)


@dataclass
class GraphSegment:
    """This"""

    artifact_name: str
    graph_segment: Graph
    all_variables: Set[str]
    input_variables: Set[str]
    return_variables: List[str]

    def __init__(
        self,
        artifact_name,
        graph_segment,
        all_variables,
        input_variables,
        return_variables,
    ) -> None:
        self.artifact_name = artifact_name
        self.graph_segment = graph_segment
        self.all_variables = all_variables
        self.input_variables = input_variables
        self.return_variables = return_variables

    def get_function_definition(self, indentation=4) -> str:
        indentation_block = " " * indentation
        artifact_code = get_source_code_from_graph(
            self.graph_segment
        ).__str__()
        artifact_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in artifact_code.split("\n")
            ]
        )

        return function_definition_template.safe_substitute(
            aname=self.artifact_name,
            args_string=", ".join([v for v in self.input_variables]),
            artifact_codeblock=artifact_codeblock,
            indentation_block=indentation_block,
            return_string=", ".join([v for v in self.return_variables]),
        )


session_module_definitaion_template = string.Template(
    """${function_definitions}

def pipeline():
${calculation_codeblock}
${indentation_block}return ${return_string}

if __name__=='__main__':
${indentation_block}pipeline()
"""
)


@dataclass
class SessionArtifacts:
    """
    Refactor a given session graph for use in a downstream task (e.g., pipeline building).
    """

    session_id: LineaID
    graph: Graph
    session_variables: List[str]
    db: RelationalLineaDB
    nx_graph: nx.DiGraph
    graph_segments: List[GraphSegment]
    artifact_list: List[LineaArtifact]
    node_context: Dict[LineaID, Dict[str, Any]]

    def __init__(self, artifacts: List[LineaArtifact]) -> None:
        self.artifact_list = artifacts
        self.session_id = artifacts[0]._session_id
        self.db = artifacts[0].db
        self.graph = artifacts[0]._get_graph()
        self.nx_graph = self.graph.nx_graph
        self.graph_segments = []
        self.node_context = OrderedDict()

        self._resolve_dependencies()
        self._slice_session_artifacts()

    def _resolve_dependencies(self):
        # Map each variable node ID to the corresponding variable name(when variable assigned)
        self.session_variables = self.db.get_variables_for_session(
            self.session_id
        )
        variable_dict: Dict[LineaID, Set[str]] = dict()
        for node_id, variable_name in self.session_variables:
            variable_dict[node_id] = (
                set([variable_name])
                if node_id not in variable_dict.keys()
                else variable_dict[node_id].union(set([variable_name]))
            )

        # Map each artifact node ID to the corresponding artifact name
        session_artifacts = self.db.get_artifacts_for_session(self.session_id)
        artifact_dict = {
            artifact.node_id: artifact.name for artifact in session_artifacts
        }

        # Identify variable dependencies of each node in topological order
        for node_id in nx.topological_sort(self.nx_graph):
            predecessors = self.nx_graph.predecessors(node_id)
            self.node_context[node_id] = {
                "assigned_variables": variable_dict.get(node_id, set()),
                "assigned_artifact": artifact_dict.get(node_id, None),
                "dependent_variables": set(),
            }
            for p_node_id in predecessors:
                # If predecessor is variable assignment use the variable, else use its dependencies
                dep = variable_dict.get(
                    p_node_id,
                    self.node_context[p_node_id]["dependent_variables"],
                )
                self.node_context[node_id][
                    "dependent_variables"
                ] = self.node_context[node_id]["dependent_variables"].union(
                    dep
                )

    def _slice_session_artifacts(self) -> None:
        # Identify artifact nodes and topologically sort them
        used_node_ids: Set[LineaID] = set()  # Track nodes that get ever used
        artifact_ordering = OrderedDict()
        for node_id, n in self.node_context.items():
            if n["assigned_artifact"] is not None and node_id in [
                art._node_id for art in self.artifact_list
            ]:
                artifact_ordering[node_id] = {
                    "artifact_name": n["assigned_artifact"],
                    "return_variables": list(
                        n["assigned_variables"]
                        if len(n["assigned_variables"]) > 0
                        else n["dependent_variables"]
                    ),
                }

                # Identify "non-overlapping" nodes that solely belong to the artifact
                artifact_slice_graph = get_slice_graph(self.graph, [node_id])
                artifact_node_ids = (
                    set(artifact_slice_graph.nx_graph.nodes) - used_node_ids
                )
                artifact_nodes = [
                    self.graph.get_node(node_id)
                    for node_id in artifact_node_ids
                ]
                artifact_ordering[node_id][
                    "nonoverlapping_graph"
                ] = self.graph.get_subgraph(
                    [n for n in artifact_nodes if n is not None]
                )

                # Update used nodes for next iteration
                used_node_ids = used_node_ids.union(artifact_node_ids)

                # Calculate the artifact's variable relations
                # dependent variables for all these nodes
                dependent_variables = set(
                    itertools.chain.from_iterable(
                        [
                            self.node_context[nid]["dependent_variables"]
                            for nid in artifact_node_ids
                        ]
                    )
                )
                # variables got assigned within these nodes
                assigned_variables = set(
                    itertools.chain.from_iterable(
                        [
                            self.node_context[nid]["assigned_variables"]
                            for nid in artifact_node_ids
                        ]
                    )
                )
                # all variables within these nodes
                artifact_ordering[node_id][
                    "all_variables"
                ] = dependent_variables.union(assigned_variables)
                # required input variables
                artifact_ordering[node_id]["input_variables"] = (
                    artifact_ordering[node_id]["all_variables"]
                    - assigned_variables
                )

                self.graph_segments.append(
                    GraphSegment(
                        artifact_name=artifact_ordering[node_id][
                            "artifact_name"
                        ],
                        graph_segment=artifact_ordering[node_id][
                            "nonoverlapping_graph"
                        ],
                        all_variables=artifact_ordering[node_id][
                            "all_variables"
                        ],
                        input_variables=artifact_ordering[node_id][
                            "input_variables"
                        ],
                        return_variables=artifact_ordering[node_id][
                            "return_variables"
                        ],
                    )
                )

        # Add extra return variables that are used for downstream artifacts to each artifact
        for i, graph_segment in enumerate(self.graph_segments):
            for p, prev_graph_segment in enumerate(self.graph_segments):
                if p < i:
                    variables_required_downstream = (
                        graph_segment.input_variables.intersection(
                            prev_graph_segment.all_variables
                        )
                    )
                    if len(variables_required_downstream) > 0:
                        prev_graph_segment.return_variables += sorted(
                            [
                                x
                                for x in variables_required_downstream
                                if x not in prev_graph_segment.return_variables
                            ]
                        )

    def get_session_module_definition(self, indentation=4) -> str:
        indentation_block = " " * indentation

        function_definitions = "\n".join(
            [
                graph_seg.get_function_definition(indentation=indentation)
                for graph_seg in self.graph_segments
            ]
        )
        calculation_codeblock = "\n".join(
            [
                f"{indentation_block}{', '.join(graph_seg.return_variables)} = get_{graph_seg.artifact_name}({','.join(graph_seg.input_variables)})"
                for graph_seg in self.graph_segments
            ]
        )
        return_string = ", ".join(
            [
                graph_seg.return_variables[0]
                for graph_seg in self.graph_segments
            ]
        )

        return session_module_definitaion_template.safe_substitute(
            indentation_block=indentation_block,
            function_definitions=function_definitions,
            calculation_codeblock=calculation_codeblock,
            return_string=return_string,
        )
