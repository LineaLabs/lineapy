import itertools
import logging
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import networkx as nx

from lineapy.api.api_classes import LineaArtifact
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    GlobalNode,
    LineaID,
    LookupNode,
    MutateNode,
    Node,
)
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
    IMPORT = 3


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
        Return a codeblock to define the function of the graph segment
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
        self, indentation=0, keep_lineapy_save=False, result_placeholder=None
    ) -> str:
        """
        Return a codeblock to call the function with return variables of the graph segment

        :param int indentation: indentation size
        :param bool keep_lineapy_save: whether do lineapy.save() after execution
        :param Optional[str] result_placeholder: if not null, append the return result to the result_placeholder
        """
        indentation_block = " " * indentation
        return_string = ", ".join(self.return_variables)
        args_string = ", ".join(sorted([v for v in self.input_variables]))

        codeblock = f"{indentation_block}{return_string} = get_{self.artifact_safename}({args_string})"
        if (
            keep_lineapy_save
            and self.segment_type == GraphSegmentType.ARTIFACT
        ):
            codeblock += f"""\n{indentation_block}lineapy.save({self.return_variables[0]}, "{self.artifact_name}")"""
        if result_placeholder is not None:
            codeblock += f"""\n{indentation_block}{result_placeholder}.append(copy.deepcopy({self.return_variables[0]}))"""

        return codeblock

    def get_import_block(self, indentation=0) -> str:
        """
        Return a code block for import statement of the graph segment
        """
        indentation_block = " " * indentation
        import_code = get_source_code_from_graph(self.graph_segment).__str__()
        import_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in import_code.split("\n")
                if len(line.strip(" ")) > 0
            ]
        )
        if len(import_codeblock) > 0:
            import_codeblock += "\n" * 2
        return import_codeblock


@dataclass
class SessionArtifacts:
    """
    Refactor a given session graph for use in a downstream task (e.g., pipeline building).
    """

    session_id: LineaID
    graph: Graph
    db: RelationalLineaDB
    nx_graph: nx.DiGraph
    artifact_segments: List[GraphSegment]
    import_segment: GraphSegment
    artifact_list: List[LineaArtifact]
    artifact_ordering: List
    artifact_dict: Dict[LineaID, Optional[str]]
    variable_dict: Dict[LineaID, Set[str]]
    import_dict: Dict[LineaID, Set[str]]
    node_context: Dict[LineaID, Dict[str, Any]]
    input_parameters: List[str]
    input_parameters_node: Dict[str, LineaID]

    def __init__(self, artifacts: List[LineaArtifact]) -> None:
        self.artifact_list = artifacts
        self.session_id = artifacts[0]._session_id
        self.db = artifacts[0].db
        self.graph = artifacts[0]._get_graph()
        self.nx_graph = self.graph.nx_graph
        self.artifact_segments = []
        self.node_context = OrderedDict()
        self.input_parameters = []

        self._update_node_context()
        self._slice_session_artifacts()

    def _is_import_node(self, node_id: LineaID) -> bool:
        """
        Given node_id, check whether it is a CallNode doing module import
        """
        node = self.graph.get_node(node_id)
        if isinstance(node, CallNode) and hasattr(node, "function_id"):
            lookup_node_id = node.__dict__.get("function_id", None)
            if lookup_node_id is not None:
                lookup_node = self.graph.get_node(lookup_node_id)
                if isinstance(lookup_node, LookupNode):
                    lookup_node_name = lookup_node.__dict__.get("name", "")
                    return lookup_node_name in ["l_import", "getattr"]
        return False

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
        module_import : module name/alias that this node is point to
        """

        # Map each variable node ID to the corresponding variable name(when variable assigned)
        # Need to treat import different from regular variable assignment
        self.variable_dict = OrderedDict()
        self.import_dict = OrderedDict()
        self.input_parameters_node = dict()
        for node_id, variable_name in self.db.get_variables_for_session(
            self.session_id
        ):
            node = self.graph.get_node(node_id)
            if self._is_import_node(node_id):
                self.import_dict[node_id] = (
                    set([variable_name])
                    if node_id not in self.import_dict.keys()
                    else self.import_dict[node_id].union(set([variable_name]))
                )
            else:
                self.variable_dict[node_id] = (
                    set([variable_name])
                    if node_id not in self.variable_dict.keys()
                    else self.variable_dict[node_id].union(
                        set([variable_name])
                    )
                )

                for var in set([variable_name]).intersection(
                    set(self.input_parameters)
                ):
                    if self.input_parameters_node.get(var, None) is not None:
                        # Duplicated variable name existing
                        raise Exception
                    else:
                        self.input_parameters_node[var] = node_id

        # Map node id to artifact assignment
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
                "module_import": self.import_dict.get(node_id, set()),
            }
            # Dependent variables of each node is union of all tracked
            # variables from predecessors
            for p_node_id in self.node_context[node_id]["predecessors"]:
                dep = self.variable_dict.get(
                    p_node_id,
                    self.node_context[p_node_id]["tracked_variables"],
                )
                self.node_context[node_id][
                    "dependent_variables"
                ] = self.node_context[node_id]["dependent_variables"].union(
                    dep
                )

            # Determine the tracked variables of each node
            # Fix me when you see return variables in refactor behaves strange
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
        Return the subgraph as LineaPy Graph from list of node id
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

        # Add user defined parameter in to input variables list
        for nid in node_list:
            if self.input_parameters_node.get(nid, None) is not None:
                involved_variables["input_variables"].add(
                    self.input_parameters_node[nid]
                )

        return involved_variables

    def _get_graph_segment_from_artifact_context(
        self, artifact_context
    ) -> GraphSegment:
        """
        Create the graphsegment from the artifact context

        Note: might be able get rid of artifact_context entirely with some more
        refactoring.
        """
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
        self.import_node_ids: Set[LineaID] = set()
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
                artifact_sliced_graph = get_slice_graph(self.graph, [node_id])
                artifact_sliced_node_list = set(
                    artifact_sliced_graph.nx_graph.nodes
                )
                # Identify import nodes(need to lift them out)
                artifact_import_node = self.import_node_ids.union(
                    set(
                        [
                            _node
                            for _node in artifact_sliced_node_list
                            if len(self.node_context[_node]["module_import"])
                            > 0
                        ]
                    )
                )
                # Ancestors of import node should be also for import
                artifact_import_node_ancestors = set(
                    itertools.chain.from_iterable(
                        [
                            self.graph.get_ancestors(import_node_id)
                            for import_node_id in artifact_import_node
                        ]
                    )
                )
                # All nodes related to import modules
                self.import_node_ids = self.import_node_ids.union(
                    (
                        artifact_import_node.union(
                            artifact_import_node_ancestors
                        )
                    ).intersection(artifact_sliced_node_list)
                    - used_node_ids
                )

                # Nodes only belong to this artifact
                artifact_context["node_list"] = (
                    artifact_sliced_node_list
                    - used_node_ids
                    - self.import_node_ids
                )

                # Update used nodes for next iteration
                used_node_ids = used_node_ids.union(
                    artifact_context["node_list"]
                ).union(self.import_node_ids)

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

                for n_id in self.import_node_ids:
                    self.node_context[n_id]["artifact_name"] = "module_import"

                # Figure out where each predecessor is coming from which artifact
                artifact_context["predecessor_nodes"] = (
                    set(
                        itertools.chain.from_iterable(
                            [
                                self.node_context[n_id]["predecessors"]
                                for n_id in artifact_context["node_list"]
                            ]
                        )
                    )
                    - set(artifact_context["node_list"])
                    - self.import_node_ids
                )

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
                            # "dependent_variables"
                            "tracked_variables"
                        ]
                    )
                    predecessor_artifact = self.node_context[pred_node_id][
                        "artifact_name"
                    ]
                    if predecessor_artifact != "module_import":
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

                    # Common variables between two artifacts
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

                # Remove input parameter node
                artifact_context["node_list"] = artifact_context[
                    "node_list"
                ] - set(self.input_parameters_node.values())

                self.artifact_ordering.append(artifact_context)

        self.import_segment = GraphSegment(
            artifact_name="",
            graph_segment=self._get_subgraph_from_node_list(
                list(self.import_node_ids)
            ),
            segment_type=GraphSegmentType.IMPORT,
            all_variables=set(),
            input_variables=set(),
            return_variables=[],
        )

        self.artifact_segments = [
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

        import_block = self.import_segment.get_import_block(indentation=0)

        function_definitions = "\n\n".join(
            [
                graph_seg.get_function_definition(indentation=indentation)
                for graph_seg in self.artifact_segments
            ]
        )

        calculation_codeblock = "\n".join(
            [
                graph_seg.get_function_call_block(
                    indentation=indentation,
                    keep_lineapy_save=keep_lineapy_save,
                    result_placeholder=None
                    if len(self.artifact_list) == 1
                    or graph_seg.segment_type != GraphSegmentType.ARTIFACT
                    else "sessionartifacts",
                )
                for graph_seg in self.artifact_segments
            ]
        )
        return_string = ", ".join(
            [
                graph_seg.return_variables[0]
                for graph_seg in self.artifact_segments
                if graph_seg.segment_type == GraphSegmentType.ARTIFACT
            ]
        )

        if len(self.artifact_list) == 1:
            module_definition_string = f"""{import_block}{function_definitions}

def pipeline():
{calculation_codeblock}
{indentation_block}return {return_string}

if __name__=="__main__":
{indentation_block}pipeline()
"""
        else:
            module_definition_string = f"""import copy
{import_block}{function_definitions}

def pipeline():
{indentation_block}sessionartifacts = []
{calculation_codeblock}
{indentation_block}return sessionartifacts

if __name__=="__main__":
{indentation_block}pipeline()
"""

        return module_definition_string
