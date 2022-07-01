import itertools
import logging
import string
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Set, Tuple, Union

import networkx as nx
from sqlalchemy import over

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
        all_variables,
        input_variables,
        return_variables,
    ) -> None:
        self.artifact_name = artifact_name
        self.artifact_safename = artifact_name  # Fix me
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

        function_definition_template = string.Template(
            """def get_${aname}(${args_string}):
${artifact_codeblock}
${indentation_block}return ${return_string}
"""
        )

        return function_definition_template.safe_substitute(
            aname=self.artifact_safename,
            args_string=", ".join([v for v in self.input_variables]),
            artifact_codeblock=artifact_codeblock,
            indentation_block=indentation_block,
            return_string=", ".join([v for v in self.return_variables]),
        )


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
    artifact_dict: OrderedDict[LineaID, str]
    variable_dict: OrderedDict[LineaID, Set[str]]
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

    def _get_subgraph_from_node_list(self, node_list: List[LineaID]) -> Graph:
        return self.graph.get_subgraph(
            [self.graph.get_node(node_id) for node_id in node_list]
        )

    def _get_involved_variables_from_node_list(
        self, node_list
    ) -> Dict[str, Set[str]]:

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
            all_variables=involved_variables["all_variables"],
            input_variables=involved_variables["input_variables"],
            return_variables=artifact_context["return_variables"],
        )

    def _slice_session_artifacts(self) -> None:
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
                    "return_variables": list(
                        n["assigned_variables"]
                        if len(n["assigned_variables"]) > 0
                        else n["dependent_variables"]
                    ),
                }

                artifact_sliced_node_list = set(
                    get_slice_graph(self.graph, [node_id]).nx_graph.nodes
                )

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

                for n_id in artifact_context["node_list"]:
                    self.node_context[n_id]["artifact_name"] = n[
                        "assigned_artifact"
                    ]

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

                for source_artifact_name, variables in artifact_context[
                    "input_variable_sources"
                ].items():
                    source_artifact_context_index, source_artifact_context = [
                        (i, context)
                        for i, context in enumerate(self.artifact_ordering)
                        if context["artifact_name"] == source_artifact_name
                    ][0]
                    print(
                        source_artifact_context_index,
                        len(self.artifact_ordering),
                    )

                    common_return_variables = set(
                        source_artifact_context["return_variables"]
                    ).intersection(
                        artifact_context["input_variable_sources"][
                            source_artifact_context["artifact_name"]
                        ]
                    )

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
                        source_art_slice_variable_graph = get_slice_graph(
                            source_art_graph,
                            [
                                n
                                for n in artifact_context["predecessor_nodes"]
                                if n in source_art_graph.nx_graph.nodes
                            ],
                        )
                        common_nodes = artifact_sliced_node_list.intersection(
                            set(source_art_slice_variable_graph.nx_graph.nodes)
                        )

                        if len(common_nodes) > 0:
                            common_artifact_variables = (
                                self._get_involved_variables_from_node_list(
                                    common_nodes
                                )
                            )
                            common_artifact_context = {
                                "artifact_name": f"{'_'.join(common_inner_variables)}_for_{artifact_context['artifact_name']}",
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

        # for prev_art in self.artifact_ordering:
        #     if (
        #         prev_art["artifact_name"]
        #         in artifact_context["input_variable_sources"].keys()
        #     ):
        #         return_variables_intersection = set(
        #             prev_art["return_variables"]
        #         ).intersection(
        #             artifact_context["input_variable_sources"][
        #                 prev_art["artifact_name"]
        #             ]
        #         )

        #         if len(return_variables_intersection) > 0:
        #             print(
        #                 artifact_context["artifact_name"],
        #                 "is taking",
        #                 return_variables_intersection,
        #                 "from return of ",
        #                 prev_art["artifact_name"],
        #             )

        #         inner_variables_intersection = (
        #             prev_art["all_variables"]
        #             - set(prev_art["return_variables"])
        #         ).intersection(
        #             artifact_context["input_variable_sources"][
        #                 prev_art["artifact_name"]
        #             ]
        #         )

        #         if len(inner_variables_intersection) > 0:
        #             print(
        #                 artifact_context["artifact_name"],
        #                 "is taking",
        #                 inner_variables_intersection,
        #                 "from inside of ",
        #                 prev_art["artifact_name"],
        #             )

        #             # print("prev artifact nodes", prev_art["node_list"])
        #             prev_art_graph = self._get_subgraph_from_node_list(
        #                 prev_art["node_list"]
        #             )
        #             prev_art_slice_variable_graph = get_slice_graph(
        #                 prev_art_graph,
        #                 [
        #                     n
        #                     for n in artifact_context[
        #                         "predecessor_nodes"
        #                     ]
        #                     if n in prev_art_graph.nx_graph.nodes
        #                 ],
        #             )
        #             intersection_nodes = artifact_sliced_node_list.intersection(
        #                 set(
        #                     prev_art_slice_variable_graph.nx_graph.nodes
        #                 )
        #             )

        #             print("common code")
        #             print(
        #                 get_source_code_from_graph(
        #                     self.graph.get_subgraph(
        #                         [
        #                             self.graph.get_node(node_id)
        #                             for node_id in intersection_nodes
        #                         ]
        #                     )
        #                 )
        #             )
        #             print("remaining code")
        #             print(
        #                 get_source_code_from_graph(
        #                     self.graph.get_subgraph(
        #                         [
        #                             self.graph.get_node(node_id)
        #                             for node_id in artifact_context[
        #                                 "node_list"
        #                             ]
        #                             if node_id
        #                             not in intersection_nodes
        #                         ]
        #                     )
        #                 )
        #             )

        # gsegment = self._get_graph_segment_from_artifact_context(
        #     artifact_context
        # )

        # input_variables = set(artifact_context["input_variables"])
        # while len(input_variables) > 0 and segment_counter <= len(
        #     self.artifact_ordering
        # ):
        #     segment = self.artifact_ordering[-segment_counter]
        #     return_variables_intersection = set(
        #         segment["return_variables"]
        #     ).intersection(input_variables)
        #     if len(return_variables_intersection) > 0:
        #         print(
        #             artifact_context["artifact_name"],
        #             input_variables,
        #             "intersect with return variables of",
        #             segment["artifact_name"],
        #             segment["return_variables"],
        #         )
        #         input_variables -= return_variables_intersection
        #     all_variables_intersection = (
        #         segment["all_variables"]
        #         - set(segment["return_variables"])
        #     ).intersection(input_variables)
        #     if len(all_variables_intersection) > 0:
        #         print(
        #             artifact_context["artifact_name"],
        #             input_variables,
        #             "intersect with inner variables of",
        #             segment["artifact_name"],
        #             segment["all_variables"]
        #             - set(segment["return_variables"]),
        #         )

        #         intersect_nodes = segment["node_list"].intersection(
        #             artifact_sliced_node_list
        #         )
        #         print("common nodes", intersect_nodes)
        #         print("common code")
        #         print(
        #             get_source_code_from_graph(
        #                 self.graph.get_subgraph(
        #                     [
        #                         self.graph.get_node(node_id)
        #                         for node_id in intersect_nodes
        #                     ]
        #                 )
        #             )
        #         )

        #         input_variables -= all_variables_intersection
        #     segment_counter += 1

        # artifact_nodes = [
        #     self.graph.get_node(node_id)
        #     for node_id in artifact_context["node_list"]
        # ]
        # artifact_context[
        #     "nonoverlapping_graph"
        # ] = self.graph.get_subgraph(
        #     [n for n in artifact_nodes if n is not None]
        # )

    #     def _slice_session_artifacts(self) -> None:
    #         # Identify artifact nodes and topologically sort them
    #         used_node_ids: Set[LineaID] = set()  # Track nodes that get ever used
    #         artifact_ordering = OrderedDict()
    #         for node_id, n in self.node_context.items():
    #             if n["assigned_artifact"] is not None and node_id in [
    #                 art._node_id for art in self.artifact_list
    #             ]:
    #                 artifact_ordering[node_id] = {
    #                     "artifact_name": n["assigned_artifact"],
    #                     "return_variables": list(
    #                         n["assigned_variables"]
    #                         if len(n["assigned_variables"]) > 0
    #                         else n["dependent_variables"]
    #                     ),
    #                 }

    #                 # Identify "non-overlapping" nodes that solely belong to the artifact
    #                 artifact_node_ids = (
    #                     set(get_slice_graph(self.graph, [node_id]).nx_graph.nodes)
    #                     - used_node_ids
    #                 )
    #                 artifact_nodes = [
    #                     self.graph.get_node(node_id)
    #                     for node_id in artifact_node_ids
    #                 ]
    #                 for n_id in artifact_node_ids:
    #                     self.node_context[n_id]["artifact_name"] = n[
    #                         "assigned_artifact"
    #                     ]

    #                 artifact_ordering[node_id][
    #                     "nonoverlapping_graph"
    #                 ] = self.graph.get_subgraph(
    #                     [n for n in artifact_nodes if n is not None]
    #                 )

    #                 # Update used nodes for next iteration
    #                 used_node_ids = used_node_ids.union(artifact_node_ids)

    #                 # Calculate the artifact's variable relations
    #                 # dependent variables for all these nodes
    #                 dependent_variables = set(
    #                     itertools.chain.from_iterable(
    #                         [
    #                             self.node_context[nid]["dependent_variables"]
    #                             for nid in artifact_node_ids
    #                         ]
    #                     )
    #                 )
    #                 # variables got assigned within these nodes
    #                 assigned_variables = set(
    #                     itertools.chain.from_iterable(
    #                         [
    #                             self.node_context[nid]["assigned_variables"]
    #                             for nid in artifact_node_ids
    #                         ]
    #                     )
    #                 )
    #                 # all variables within these nodes
    #                 artifact_ordering[node_id][
    #                     "all_variables"
    #                 ] = dependent_variables.union(assigned_variables)
    #                 # required input variables
    #                 artifact_ordering[node_id]["input_variables"] = (
    #                     artifact_ordering[node_id]["all_variables"]
    #                     - assigned_variables
    #                 )

    #                 self.graph_segments.append(
    #                     GraphSegment(
    #                         artifact_name=artifact_ordering[node_id][
    #                             "artifact_name"
    #                         ],
    #                         graph_segment=artifact_ordering[node_id][
    #                             "nonoverlapping_graph"
    #                         ],
    #                         all_variables=artifact_ordering[node_id][
    #                             "all_variables"
    #                         ],
    #                         input_variables=artifact_ordering[node_id][
    #                             "input_variables"
    #                         ],
    #                         return_variables=artifact_ordering[node_id][
    #                             "return_variables"
    #                         ],
    #                     )
    #                 )

    #         # Add extra return variables that are used for downstream artifacts to each artifact
    #         for i, graph_segment in enumerate(self.graph_segments):
    #             for p, prev_graph_segment in enumerate(self.graph_segments):
    #                 if p < i:
    #                     variables_required_downstream = (
    #                         graph_segment.input_variables.intersection(
    #                             prev_graph_segment.all_variables
    #                         )
    #                     )
    #                     if len(variables_required_downstream) > 0:
    #                         prev_graph_segment.return_variables += sorted(
    #                             [
    #                                 x
    #                                 for x in variables_required_downstream
    #                                 if x not in prev_graph_segment.return_variables
    #                             ]
    #                         )

    #         # # Add extra return variables that are used for downstream artifacts to each artifact
    #         # for i, graph_segment in enumerate(self.graph_segments):
    #         #     for p, prev_graph_segment in enumerate(self.graph_segments):
    #         #         if p < i:
    #         #             extra_variables_to_return = (
    #         #                 graph_segment.input_variables.intersection(
    #         #                     prev_graph_segment.all_variables
    #         #                 )
    #         #                 - set(prev_graph_segment.return_variables)
    #         #             )

    #         #             if len(extra_variables_to_return) > 0:

    #         # for i, graph_segment in enumerate(self.graph_segments):
    #         #     for p, prev_graph_segment in reversed(
    #         #         list(enumerate(self.graph_segments))
    #         #     ):
    #         #         if p < i and any(
    #         #             [
    #         #                 v in prev_graph_segment.return_variables[1:]
    #         #                 for v in graph_segment.input_variables
    #         #             ]
    #         #         ):
    #         #             common_variables = (
    #         #                 graph_segment.input_variables.intersection(
    #         #                     set(prev_graph_segment.return_variables)
    #         #                 )
    #         #             )

    #         #             common_nodes = list(
    #         #                 nx.intersection_all(
    #         #                     [
    #         #                         prev_graph_segment.graph_segment.nx_graph,
    #         #                         get_slice_graph(
    #         #                             self.graph,
    #         #                             list(
    #         #                                 graph_segment.graph_segment.nx_graph.nodes
    #         #                             ),
    #         #                         ).nx_graph,
    #         #                     ]
    #         #                 ).nodes
    #         #             )

    #         #             prev_artifact_id = [
    #         #                 art._node_id
    #         #                 for art in self.artifact_list
    #         #                 if art.name == prev_graph_segment.artifact_name
    #         #             ]

    #         #             # Check whether common nodes include the previous artifact node (if yes, no refactor possible)6
    #         #             if (
    #         #                 len(prev_artifact_id) > 0
    #         #                 and prev_artifact_id[0] not in common_nodes
    #         #             ) and len(common_nodes) > 0:

    #         #                 print(
    #         #                     graph_segment.artifact_name,
    #         #                     graph_segment.input_variables,
    #         #                     "need to extract",
    #         #                     common_variables,
    #         #                     "from",
    #         #                     prev_graph_segment.artifact_name,
    #         #                     prev_graph_segment.return_variables,
    #         #                 )

    #         #                 print("prev graph segment code")
    #         #                 print(
    #         #                     get_source_code_from_graph(
    #         #                         prev_graph_segment.graph_segment
    #         #                     )
    #         #                 )

    #         #                 common_graph = self.graph.get_subgraph(
    #         #                     [
    #         #                         self.graph.get_node(nodeid)
    #         #                         for nodeid in common_nodes
    #         #                     ]
    #         #                 )

    #         #                 print(
    #         #                     set(common_nodes)
    #         #                     - set(
    #         #                         prev_graph_segment.graph_segment.nx_graph.nodes
    #         #                     )
    #         #                 )

    #         #                 print(
    #         #                     set(common_graph.nx_graph.nodes)
    #         #                     - set(
    #         #                         prev_graph_segment.graph_segment.nx_graph.nodes
    #         #                     )
    #         #                 )

    #         #                 common_code = get_source_code_from_graph(common_graph)

    #         #                 print("common code")
    #         #                 print(common_code)
    #         #                 print("-" * 80)

    def get_session_module_definition(
        self, indentation: int = 4, keep_lineapy_save: bool = False
    ) -> str:
        """
        Generate pipeline at session level
        """

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
                if not keep_lineapy_save
                else f"""{indentation_block}{', '.join(graph_seg.return_variables)} = get_{graph_seg.artifact_name}({','.join(graph_seg.input_variables)})
{indentation_block}lineapy.save({graph_seg.return_variables[0]}, '{graph_seg.artifact_name}')"""
                for graph_seg in self.graph_segments
            ]
        )
        return_string = ", ".join(
            [
                graph_seg.return_variables[0]
                for graph_seg in self.graph_segments
            ]
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

        return session_module_definitaion_template.safe_substitute(
            indentation_block=indentation_block,
            function_definitions=function_definitions,
            calculation_codeblock=calculation_codeblock,
            return_string=return_string,
        )
