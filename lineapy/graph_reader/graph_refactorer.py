import itertools
import logging
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import networkx as nx

from lineapy.api.api_classes import LineaArtifact
from lineapy.data.graph import Graph
from lineapy.data.types import CallNode, GlobalNode, LineaID, MutateNode, Node
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import (
    get_slice_graph,
    get_source_code_from_graph,
)
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


class GraphSegmentType(Enum):
    """
    GraphSegment type to identify the purpose of the graph segment
    - ARTIFACT : the segment returns an artifact
    - HELPER : the segment returns variables used in multiple artifacts
    """

    ARTIFACT = 1
    COMMON_VARIABLE = 2


@dataclass
class GraphSegment:
    """
    This class contains information required to wrap a lineapy Graph object as a function
    """

    artifact_name: str
    artifact_safename: str
    graph_segment: Graph
    segment_type: GraphSegmentType
    all_variables: Set[str]
    input_variables: Set[str]
    return_variables: List[str]

    def __init__(
        self,
        artifact_name,
        graph_segment,
        segment_type,
        all_variables,
        input_variables,
        return_variables,
    ) -> None:
        self.artifact_name = artifact_name
        self.artifact_safename = artifact_name.replace(" ", "")
        self.graph_segment = graph_segment
        self.segment_type = segment_type
        self.all_variables = all_variables
        self.input_variables = input_variables
        self.return_variables = return_variables

    def get_function_definition(self, indentation=4) -> str:
        """
        Return a codeblock to define the function
        """
        indentation_block = " " * indentation
        artifact_code = get_source_code_from_graph(
            self.graph_segment
        ).__str__()
        artifact_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in artifact_code.split("\n")
                if len(line.strip(" ")) > 0
            ]
        )
        artifact_name = self.artifact_safename
        args_string = ", ".join(sorted([v for v in self.input_variables]))
        return_string = ", ".join([v for v in self.return_variables])

        return f"def get_{artifact_name}({args_string}):\n{artifact_codeblock}\n{indentation_block}return {return_string}"

    def get_function_call_block(
        self, indentation=0, keep_lineapy_save=False
    ) -> str:
        """
        Return a codeblock to call the function with return variables
        """
        indentation_block = " " * indentation
        return_string = ", ".join(self.return_variables)
        args_string = ", ".join(sorted([v for v in self.input_variables]))

        codeblock = f"{indentation_block}{return_string} = get_{self.artifact_safename}({args_string})"
        # print(self.artifact_safename, self.segment_type)
        if (
            keep_lineapy_save
            and self.segment_type == GraphSegmentType.ARTIFACT
        ):
            codeblock += f"""\n{indentation_block}lineapy.save({self.return_variables[0]}, "{self.artifact_name}")"""

        return codeblock


@dataclass
class SessionArtifacts:
    """
    Refactor a given session graph for use in a downstream task (e.g., pipeline building).
    """

    session_id: LineaID
    graph: Graph
    db: RelationalLineaDB
    nx_graph: nx.DiGraph
    graph_segments: List[GraphSegment]
    artifact_list: List[LineaArtifact]
    artifact_ordering: List
    artifact_dict: Dict[LineaID, Optional[str]]
    variable_dict: Dict[LineaID, Set[str]]
    node_context: Dict[LineaID, Dict[str, Any]]

    def __init__(self, artifacts: List[LineaArtifact]) -> None:
        self.artifact_list = artifacts
        self.session_id = artifacts[0]._session_id
        self.db = artifacts[0].db
        self.graph = artifacts[0]._get_graph()
        self.nx_graph = self.graph.nx_graph
        self.graph_segments = []
        self.node_context = OrderedDict()

        self._update_node_context()
        self._slice_session_artifacts()

    def _update_node_context(self):
        """
        Traverse every node within the session in topologically sorted order and update
        node_context with following informations

        assigned_variables : variables assigned at this node
        assigned_artifact : this node is pointing to some artifact
        predecessors : predecessors of the node
        dependent_variables : union of if any variable is assigned at predecessor node,
            use the assigned variables; otherwise, use the dependent_variables
        tracked_variables : variables that this node is point to
        """

        # Map each variable node ID to the corresponding variable name(when variable assigned)
        self.variable_dict = OrderedDict()
        for node_id, variable_name in self.db.get_variables_for_session(
            self.session_id
        ):
            self.variable_dict[node_id] = (
                set([variable_name])
                if node_id not in self.variable_dict.keys()
                else self.variable_dict[node_id].union(set([variable_name]))
            )

        # Map each artifact node ID to the corresponding artifact name
        self.artifact_dict = {
            artifact.node_id: artifact.name
            for artifact in self.db.get_artifacts_for_session(self.session_id)
        }

        # Identify variable dependencies of each node in topological order
        for node_id in nx.topological_sort(self.nx_graph):
            self.node_context[node_id] = {
                "assigned_variables": self.variable_dict.get(node_id, set()),
                "assigned_artifact": self.artifact_dict.get(node_id, None),
                "dependent_variables": set(),
                "predecessors": set(self.nx_graph.predecessors(node_id)),
                "tracked_variables": set(),
            }
            for p_node_id in self.node_context[node_id]["predecessors"]:
                # If predecessor is variable assignment use the variable; otherwise, use its dependencies.
                dep = self.variable_dict.get(
                    p_node_id,
                    self.node_context[p_node_id]["dependent_variables"],
                )
                self.node_context[node_id][
                    "dependent_variables"
                ] = self.node_context[node_id]["dependent_variables"].union(
                    dep
                )

            # Edit me when you see return variables in refactor behaves strange
            node = self.graph.get_node(node_id=node_id)
            if len(self.node_context[node_id]["assigned_variables"]) > 0:
                self.node_context[node_id][
                    "tracked_variables"
                ] = self.node_context[node_id]["assigned_variables"]
            elif isinstance(node, MutateNode) or isinstance(node, GlobalNode):
                predecessor_call_id = node.call_id
                if (
                    predecessor_call_id
                    in self.node_context[node_id]["predecessors"]
                ):
                    self.node_context[node_id][
                        "tracked_variables"
                    ] = self.node_context[predecessor_call_id][
                        "tracked_variables"
                    ]
            elif isinstance(node, CallNode):
                if (
                    len(node.global_reads) > 0
                    and list(node.global_reads.values())[0]
                    in self.node_context[node_id]["predecessors"]
                ):
                    self.node_context[node_id][
                        "tracked_variables"
                    ] = self.node_context[list(node.global_reads.values())[0]][
                        "tracked_variables"
                    ]
                elif (
                    node.function_id
                    in self.node_context[node_id]["predecessors"]
                    and len(
                        self.node_context[node.function_id][
                            "dependent_variables"
                        ]
                    )
                    > 0
                ):
                    self.node_context[node_id][
                        "tracked_variables"
                    ] = self.node_context[node.function_id][
                        "tracked_variables"
                    ]
                elif (
                    len(node.positional_args) > 0
                    and node.positional_args[0].id
                    in self.node_context[node_id]["predecessors"]
                ):
                    self.node_context[node_id][
                        "tracked_variables"
                    ] = self.node_context[node.positional_args[0].id][
                        "tracked_variables"
                    ]
                else:
                    self.node_context[node_id]["tracked_variables"] = set()
            else:
                self.node_context[node_id]["tracked_variables"] = set()

    def _get_subgraph_from_node_list(self, node_list: List[LineaID]) -> Graph:
        """
        Return the subgraph from list of node id
        """

        # Fix me, ugly code to satisfy type checking
        nodes: List[Node] = []
        for node_id in node_list:
            node = self.graph.get_node(node_id)
            if node is not None:
                nodes.append(node)

        return self.graph.get_subgraph(nodes)

    def _get_involved_variables_from_node_list(
        self, node_list
    ) -> Dict[str, Set[str]]:
        """
        How each variables are involved within these nodes.

        Return a dictionary with following keys
        dependent_variables : union of all dependent_variables of each node
        assigned_variables : union of all assigned_variables of each node
        all_variables : union of dependent_variables and assigned_variables
        input_variables : all_variables - assigned_variables
        """

        involved_variables = dict()
        involved_variables["dependent_variables"] = set(
            itertools.chain.from_iterable(
                [
                    self.node_context[nid]["dependent_variables"]
                    for nid in node_list
                ]
            )
        )
        # variables got assigned within these nodes
        involved_variables["assigned_variables"] = set(
            itertools.chain.from_iterable(
                [
                    self.node_context[nid]["assigned_variables"]
                    for nid in node_list
                ]
            )
        )
        # all variables within these nodes
        involved_variables["all_variables"] = involved_variables[
            "dependent_variables"
        ].union(involved_variables["assigned_variables"])
        # required input variables
        involved_variables["input_variables"] = (
            involved_variables["all_variables"]
            - involved_variables["assigned_variables"]
        )

        return involved_variables

    def _get_graph_segment_from_artifact_context(
        self, artifact_context
    ) -> GraphSegment:
        subgraph = self._get_subgraph_from_node_list(
            artifact_context["node_list"]
        )
        involved_variables = self._get_involved_variables_from_node_list(
            artifact_context["node_list"]
        )
        return GraphSegment(
            artifact_name=artifact_context["artifact_name"],
            graph_segment=subgraph,
            segment_type=artifact_context["artifact_type"],
            all_variables=involved_variables["all_variables"],
            input_variables=involved_variables["input_variables"],
            return_variables=artifact_context["return_variables"],
        )

    def _slice_session_artifacts(self) -> None:
        """
        Iterate over artifacts in topological sorted order(on artifact node id).
        Assigned nodes of artifact sliced graph to the artifact context for
        those nodes that are not belong to prior artifacts. For each node,
        update the artifact_name in node_context.
        For union of all predecessor nodes, if the predecessor node comes from
        previous artifact. Find the common nodes of current artifact subgraph and
        sliced graph to the predecessor node in the predecessor artifact.
        If there are common nodes between the two graphs, we need to break the
        graph of predecessor artifact into two pieces. One for common variables,
        the other for the artifact itself.
        """
        used_node_ids: Set[LineaID] = set()  # Track nodes that get ever used
        self.artifact_ordering = list()
        for node_id, n in self.node_context.items():
            if n["assigned_artifact"] is not None and node_id in [
                art._node_id for art in self.artifact_list
            ]:
                artifact_context = {
                    "node_id": node_id,
                    "artifact_type": GraphSegmentType.ARTIFACT,
                    "artifact_name": n["assigned_artifact"],
                    "tracked_variables": n["tracked_variables"],
                    "return_variables": list(n["tracked_variables"]),
                }

                # All nodes related to this artifact
                artifact_sliced_node_list = set(
                    get_slice_graph(self.graph, [node_id]).nx_graph.nodes
                )

                # Nodes only belong to this artifact
                artifact_context["node_list"] = (
                    set(get_slice_graph(self.graph, [node_id]).nx_graph.nodes)
                    - used_node_ids
                )

                # Update used nodes for next iteration
                used_node_ids = used_node_ids.union(
                    artifact_context["node_list"]
                )

                artifact_context = {
                    **artifact_context,
                    **self._get_involved_variables_from_node_list(
                        artifact_context["node_list"]
                    ),
                }

                # Update node context to label the node is assigned to this artifact
                for n_id in artifact_context["node_list"]:
                    self.node_context[n_id]["artifact_name"] = n[
                        "assigned_artifact"
                    ]

                # Figure out where each predecessor is coming from which artifact
                artifact_context["predecessor_nodes"] = set(
                    itertools.chain.from_iterable(
                        [
                            self.node_context[n_id]["predecessors"]
                            for n_id in artifact_context["node_list"]
                        ]
                    )
                ) - set(artifact_context["node_list"])

                artifact_context["predecessor_artifact"] = set(
                    [
                        self.node_context[n_id]["artifact_name"]
                        for n_id in artifact_context["predecessor_nodes"]
                    ]
                )

                # Get information about which input variable is originated from which artifact
                artifact_context["input_variable_sources"] = dict()
                for pred_node_id in artifact_context["predecessor_nodes"]:
                    predecessor_variables = (
                        self.node_context[pred_node_id]["assigned_variables"]
                        if len(
                            self.node_context[pred_node_id][
                                "assigned_variables"
                            ]
                        )
                        > 0
                        else self.node_context[pred_node_id][
                            "dependent_variables"
                        ]
                    )
                    predecessor_artifact = self.node_context[pred_node_id][
                        "artifact_name"
                    ]
                    artifact_context["input_variable_sources"][
                        predecessor_artifact
                    ] = (
                        artifact_context["input_variable_sources"]
                        .get(predecessor_artifact, set())
                        .union(predecessor_variables)
                    )

                # Check whether we need to breakdown existing artifact graph
                # segment. If the precedent node in precedent artifact graph
                # is not the artifact itself, this means we should split the
                # existing artifact graph segment.
                for source_artifact_name, variables in artifact_context[
                    "input_variable_sources"
                ].items():
                    source_artifact_context_index, source_artifact_context = [
                        (i, context)
                        for i, context in enumerate(self.artifact_ordering)
                        if context["artifact_name"] == source_artifact_name
                    ][0]

                    common_inner_variables = (
                        source_artifact_context["all_variables"]
                        - set(source_artifact_context["return_variables"])
                    ).intersection(
                        artifact_context["input_variable_sources"][
                            source_artifact_context["artifact_name"]
                        ]
                    )
                    if len(common_inner_variables) > 0:
                        source_art_graph = self._get_subgraph_from_node_list(
                            source_artifact_context["node_list"]
                        )
                        slice_variable_nodes = [
                            n
                            for n in artifact_context["predecessor_nodes"]
                            if n in source_art_graph.nx_graph.nodes
                            and self.node_context[n]["assigned_artifact"]
                            != self.node_context[n]["artifact_name"]
                        ]
                        source_art_slice_variable_graph = get_slice_graph(
                            source_art_graph, slice_variable_nodes
                        )
                        common_nodes = artifact_sliced_node_list.intersection(
                            set(source_art_slice_variable_graph.nx_graph.nodes)
                        )

                        # Split one artifact_context into two
                        if len(common_nodes) > 0:
                            common_artifact_variables = (
                                self._get_involved_variables_from_node_list(
                                    common_nodes
                                )
                            )
                            common_artifact_context = {
                                "artifact_name": f"{'_'.join(common_inner_variables)}_for_artifact_{source_artifact_context['artifact_name']}_and_downstream",
                                "artifact_type": GraphSegmentType.COMMON_VARIABLE,
                                "node_list": common_nodes,
                                "input_variables": common_artifact_variables[
                                    "input_variables"
                                ],
                                "all_variables": common_artifact_variables[
                                    "all_variables"
                                ],
                                "return_variables": list(
                                    common_inner_variables
                                ),
                            }

                            remaining_nodes = source_artifact_context[
                                "node_list"
                            ].difference(common_nodes)
                            remaining_artifact_variables = (
                                self._get_involved_variables_from_node_list(
                                    remaining_nodes
                                )
                            )
                            remaining_artifact_context = {
                                "node_id": source_artifact_context["node_id"],
                                "artifact_name": source_artifact_context[
                                    "artifact_name"
                                ],
                                "artifact_type": GraphSegmentType.ARTIFACT,
                                "node_list": remaining_nodes,
                                "input_variables": remaining_artifact_variables[
                                    "input_variables"
                                ],
                                "all_variables": remaining_artifact_variables[
                                    "all_variables"
                                ],
                                "return_variables": source_artifact_context[
                                    "return_variables"
                                ],
                            }

                            self.artifact_ordering = (
                                self.artifact_ordering[
                                    :source_artifact_context_index
                                ]
                                + [
                                    common_artifact_context,
                                    remaining_artifact_context,
                                ]
                                + self.artifact_ordering[
                                    (source_artifact_context_index + 1) :
                                ]
                            )

                self.artifact_ordering.append(artifact_context)

        self.graph_segments = [
            self._get_graph_segment_from_artifact_context(artifact_context)
            for artifact_context in self.artifact_ordering
        ]

    def get_session_module_definition(
        self, indentation: int = 4, keep_lineapy_save: bool = False
    ) -> str:
        """
        Generate pipeline at session level
        """

        indentation_block = " " * indentation

        function_definitions = "\n\n".join(
            [
                graph_seg.get_function_definition(indentation=indentation)
                for graph_seg in self.graph_segments
            ]
        )

        calculation_codeblock = "\n".join(
            [
                graph_seg.get_function_call_block(
                    indentation=indentation,
                    keep_lineapy_save=keep_lineapy_save,
                )
                for graph_seg in self.graph_segments
            ]
        )
        return_string = ", ".join(
            [
                graph_seg.return_variables[0]
                for graph_seg in self.graph_segments
                if graph_seg.segment_type == GraphSegmentType.ARTIFACT
            ]
        )

        return f"""{function_definitions}

def pipeline():
{calculation_codeblock}
{indentation_block}return {return_string}

if __name__=="__main__":
{indentation_block}pipeline()
"""
