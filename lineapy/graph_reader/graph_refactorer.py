import itertools
import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

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
    - COMMON_VARIABLE : the segment returns variables used in multiple artifacts
    - IMPORT : the segment with module import
    - INPUT_VARIABLE : the segment for input variables
    """

    ARTIFACT = 1
    COMMON_VARIABLE = 2
    IMPORT = 3
    INPUT_PARAMETERS = 4


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
    raw_codeblock: str

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
        self.raw_codeblock = get_source_code_from_graph(
            self.graph_segment
        ).__str__()
        self.is_empty = self.raw_codeblock == ""

    def get_function_definition(self, indentation=4) -> str:
        """
        Return a codeblock to define the function of the graph segment
        """

        indentation_block = " " * indentation
        artifact_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in self.raw_codeblock.split("\n")
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
        if self.is_empty:
            return ""

        indentation_block = " " * indentation
        import_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in self.raw_codeblock.split("\n")
                if len(line.strip(" ")) > 0
            ]
        )
        if len(import_codeblock) > 0:
            import_codeblock += "\n" * 2
        return import_codeblock

    def get_input_parameters_block(self, indentation=4) -> str:
        """
        Return a code block for input parameters of the graph segment
        """
        if self.is_empty:
            return ""

        indentation_block = " " * indentation
        input_parameters_lines = self.raw_codeblock.rstrip("\n").split("\n")

        if len(input_parameters_lines) > 1:
            input_parameters_codeblock = "\n" + "".join(
                [
                    f"{indentation_block}{line},\n"
                    for line in input_parameters_lines
                ]
            )
        elif len(input_parameters_lines) == 1:
            input_parameters_codeblock = input_parameters_lines[0]
        else:
            input_parameters_codeblock = ""

        return input_parameters_codeblock


@dataclass
class NodeInfo:
    assigned_variables: Set[str] = field(default_factory=set)
    assigned_artifact: Optional[str] = field(default=None)
    dependent_variables: Set[str] = field(default_factory=set)
    predecessors: Set[int] = field(default_factory=set)
    tracked_variables: Set[str] = field(default_factory=set)
    module_import: Set[str] = field(default_factory=set)
    artifact_name: Optional[str] = field(default=None)


@dataclass
class NodeCollectionInfo:
    collection_type: GraphSegmentType

    node_list: Set[LineaID] = field(default_factory=set)

    assigned_variables: Set[str] = field(default_factory=set)
    dependent_variables: Set[str] = field(default_factory=set)
    all_variables: Set[str] = field(default_factory=set)
    input_variables: Set[str] = field(default_factory=set)

    artifact_node_id: Optional[LineaID] = field(default=None)
    artifact_name: Optional[str] = field(default=None)
    tracked_variables: Set[str] = field(default_factory=set)
    # Need to be a list to keep return order
    return_variables: List[str] = field(default_factory=list)

    predecessor_nodes: Set[LineaID] = field(default_factory=set)
    predecessor_artifact: Set[str] = field(default_factory=set)

    input_variable_sources: Dict[str, Set[str]] = field(default_factory=dict)

    artifact_safename: Optional[str] = field(default=None)
    graph_segment: Optional[Graph] = field(default=None)

    raw_codeblock: str = field(default="")

    def __init__(self, node_list: Set[LineaID]):
        self.node_list = node_list

    def _update_variable_info(self, node_context, input_parameters_node):
        self.dependent_variables = self.dependent_variables.union(
            [node_context[nid].dependent_variables for nid in self.node_list]
        )
        # variables got assigned within these nodes
        self.assigned_variables = self.assigned_variables.union(
            [node_context[nid].assigned_variables for nid in self.node_list]
        )
        # all variables within these nodes
        self.all_variables = self.dependent_variables.union(
            self.assigned_variables
        )
        # required input variables
        self.input_variables = self.all_variables - self.assigned_variables
        # Add user defined parameter in to input variables list
        self.input_variables = self.input_variables.union(
            set(
                [
                    input_parameters_node[nid]
                    for nid in self.node_list
                    if nid in input_parameters_node.keys()
                ]
            )
        )

    def _update_graph(self, graph: Graph):
        self.graph_segment = graph.get_subgraph_from_id(self.node_list)


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
    node_context: Dict[LineaID, NodeInfo]
    input_parameters: List[str]
    input_parameters_node: Dict[str, LineaID]

    def __init__(
        self, artifacts: List[LineaArtifact], input_parameters: List[str] = []
    ) -> None:
        self.artifact_list = artifacts
        self.session_id = artifacts[0]._session_id
        self.db = artifacts[0].db
        self.graph = artifacts[0]._get_graph()
        self.nx_graph = self.graph.nx_graph
        self.artifact_segments = []
        self.node_context = OrderedDict()
        self.input_parameters = input_parameters

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

    def _update_dependent_variables(
        self, nodeinfo: NodeInfo, variable_dict: Dict[str, Set[str]]
    ) -> NodeInfo:
        # Dependent variables of each node is union of all tracked
        # variables from predecessors
        for prev_node_id in nodeinfo.predecessors:
            prev_nodeinfo = self.node_context[prev_node_id]
            dep = variable_dict.get(
                prev_node_id,
                prev_nodeinfo.tracked_variables,
            )
            nodeinfo.dependent_variables = nodeinfo.dependent_variables.union(
                dep
            )
        return nodeinfo

    def _update_tracked_variables(
        self, nodeinfo: NodeInfo, node_id: LineaID
    ) -> NodeInfo:
        # Determine the tracked variables of each node
        # Fix me when you see return variables in refactor behaves strange
        node = self.graph.get_node(node_id=node_id)
        if len(nodeinfo.assigned_variables) > 0:
            nodeinfo.tracked_variables = nodeinfo.assigned_variables
        elif isinstance(node, MutateNode) or isinstance(node, GlobalNode):
            predecessor_call_id = node.call_id
            if predecessor_call_id in nodeinfo["predecessors"]:
                predecessor_nodeinfo = self.node_context[predecessor_call_id]
                nodeinfo.tracked_variables = (
                    predecessor_nodeinfo.tracked_variables
                )
        elif isinstance(node, CallNode):
            if (
                len(node.global_reads) > 0
                and list(node.global_reads.values())[0]
                in nodeinfo.predecessors
            ):
                nodeinfo.tracked_variables = self.node_context[
                    list(node.global_reads.values())[0]
                ].tracked_variables
            elif (
                node.function_id in nodeinfo.predecessors
                and len(
                    self.node_context[node.function_id].dependent_variables
                )
                > 0
            ):
                nodeinfo.tracked_variables = self.node_context[
                    node.function_id
                ].tracked_variables
            elif (
                len(node.positional_args) > 0
                and node.positional_args[0].id in nodeinfo.predecessors
            ):
                nodeinfo.tracked_variables = self.node_context[
                    node.positional_args[0].id
                ].tracked_variables
            else:
                nodeinfo.tracked_variables = set()
        else:
            nodeinfo.tracked_variables = set()
        return nodeinfo

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
        variable_dict: Dict[LineaID, Set[str]] = OrderedDict()
        import_dict = OrderedDict()
        self.input_parameters_node = dict()
        for node_id, variable_name in self.db.get_variables_for_session(
            self.session_id
        ):
            node = self.graph.get_node(node_id)
            if self._is_import_node(node_id):
                import_dict[node_id] = (
                    set([variable_name])
                    if node_id not in import_dict.keys()
                    else import_dict[node_id].union(set([variable_name]))
                )
            else:
                variable_dict[node_id] = (
                    set([variable_name])
                    if node_id not in variable_dict.keys()
                    else variable_dict[node_id].union(set([variable_name]))
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
        artifact_dict = {
            artifact.node_id: artifact.name
            for artifact in self.db.get_artifacts_for_session(self.session_id)
        }

        # Identify variable dependencies of each node in topological order
        for node_id in nx.topological_sort(self.nx_graph):

            nodeinfo = NodeInfo(
                assigned_variables=variable_dict.get(node_id, set()),
                assigned_artifact=artifact_dict.get(node_id, None),
                dependent_variables=set(),
                predecessors=set(self.nx_graph.predecessors(node_id)),
                tracked_variables=set(),
                module_import=import_dict.get(node_id, set()),
            )

            nodeinfo = self._update_dependent_variables(
                nodeinfo, variable_dict
            )

            nodeinfo = self._update_tracked_variables(nodeinfo, node_id)

            self.node_context[node_id] = nodeinfo

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

    def _get_variable_information(self, node_list) -> Dict[str, Set[str]]:
        """
        How each variables are involved within these nodes.

        Return a dictionary with following keys
        dependent_variables : union of all dependent_variables of each node
        assigned_variables : union of all assigned_variables of each node
        all_variables : union of dependent_variables and assigned_variables
        input_variables : all_variables - assigned_variables
        """

        var_info = dict()
        var_info["dependent_variables"] = set(
            itertools.chain.from_iterable(
                [
                    self.node_context[nid]["dependent_variables"]
                    for nid in node_list
                ]
            )
        )
        # variables got assigned within these nodes
        var_info["assigned_variables"] = set(
            itertools.chain.from_iterable(
                [
                    self.node_context[nid]["assigned_variables"]
                    for nid in node_list
                ]
            )
        )
        # all variables within these nodes
        var_info["all_variables"] = var_info["dependent_variables"].union(
            var_info["assigned_variables"]
        )
        # required input variables
        var_info["input_variables"] = (
            var_info["all_variables"] - var_info["assigned_variables"]
        )

        # Add user defined parameter in to input variables list
        for nid in node_list:
            if self.input_parameters_node.get(nid, None) is not None:
                var_info["input_variables"].add(
                    self.input_parameters_node[nid]
                )

        return var_info

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
        var_info = self._get_variable_information(
            artifact_context["node_list"]
        )
        # If the return variable is assigned(only in the code block)
        # and parameterized, it will not be in var_info["all_variables"]
        all_variables = var_info["all_variables"].union(
            set(artifact_context["return_variables"])
        )
        input_variables = all_variables - var_info["assigned_variables"]
        return GraphSegment(
            artifact_name=artifact_context["artifact_name"],
            graph_segment=subgraph,
            segment_type=artifact_context["artifact_type"],
            all_variables=all_variables,
            input_variables=input_variables,
            return_variables=artifact_context["return_variables"],
        )

    # def _get_import_nodes(self, nodes: Set[LineaID]) -> Set[LineaID]:
    #     importnodes = [
    #         _node
    #         for _node in nodes
    #         if len(self.node_context[_node].module_import) > 0
    #     ]
    #     # Ancestors of import node should be also for import
    #     importnodes = set(importnodes).union(
    #         *[
    #             self.graph.get_ancestors(import_node_id)
    #             for import_node_id in importnodes
    #         ]
    #     )
    #     # Ancestors might not in nodes
    #     importnodes = importnodes.intersection(nodes)
    #     return importnodes

    def _get_sliced_nodes(
        self, node_id: LineaID
    ) -> Tuple[Set[LineaID], Set[LineaID]]:
        nodes = set(get_slice_graph(self.graph, [node_id]).nx_graph.nodes)

        importnodes = [
            _node
            for _node in nodes
            if len(self.node_context[_node].module_import) > 0
        ]
        # Ancestors of import node should be also for import
        importnodes = set(importnodes).union(
            *[
                self.graph.get_ancestors(import_node_id)
                for import_node_id in importnodes
            ]
        )
        # Ancestors might not in nodes
        importnodes = importnodes.intersection(nodes)
        return nodes, importnodes

    def _get_predecessor_info(self, )

    def _slice_session_artifacts(self) -> None:
        used_nodes: Set[LineaID] = set()  # Track nodes that get ever used
        import_nodes: Set[LineaID] = set()
        self.artifact_ordering = list()
        for node_id, n in self.node_context.items():
            if n.assigned_artifact is not None and node_id in [
                art._node_id for art in self.artifact_list
            ]:
                (
                    sliced_nodes,
                    sliced_importnodes,
                ) = self._get_sliced_nodes(node_id)
                import_nodes = import_nodes.union(
                    sliced_importnodes - used_nodes
                )
                art_nodes = sliced_nodes - used_nodes - import_nodes
                used_nodes += art_nodes + import_nodes

                # Update node context to label the node is assigned to this artifact
                for n_id in nodecollectioninfo.node_list:
                    self.node_context[n_id].artifact_name = n.assigned_artifact
                for n_id in import_nodes:
                    self.node_context[n_id].artifact_name = "module_import"

                # Figure out where each predecessor is coming from which artifact
                predecessor_nodes = (
                    set().union(
                        *[
                            self.node_context[n_id].predecessors
                            for n_id in art_nodes
                        ]
                    )
                    - art_nodes
                    - import_nodes
                )

                predecessor_artifact = set(
                    [
                        self.node_context[n_id].artifact_name
                        for n_id in predecessor_nodes
                    ]
                )

                # Get information about which input variable is originated from which artifact
                input_variable_sources: Dict[str, Set[str]] = dict()
                for prev_id in predecessor_nodes:
                    prev_variables = (
                        self.node_context[prev_id].assigned_variables
                        if len(self.node_context[prev_id].assigned_variables)
                        > 0
                        else self.node_context[prev_id].tracked_variables
                    )
                    prev_art = self.node_context[prev_id].artifact_name
                    if prev_art != "module_import":
                        input_variable_sources[
                            prev_art
                        ] = input_variable_sources.get(prev_art, set()).union(
                            prev_variables
                        )

                nodecollectioninfo = NodeCollectionInfo(
                    collection_type=GraphSegmentType.ARTIFACT,
                    artifact_node_id=node_id,
                    artifact_name=n.assigned_artifact,
                    tracked_variables=n.tracked_variables,
                    return_variables=list(n.tracked_variables),
                    node_list=art_nodes,
                    predecessor_nodes=predecessor_nodes,
                    predecessor_artifact=predecessor_artifact,
                    input_variable_sources=input_variable_sources,
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
        used_nodes: Set[LineaID] = set()  # Track nodes that get ever used
        import_nodes: Set[LineaID] = set()
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
                art_sliced_graph = get_slice_graph(self.graph, [node_id])
                art_sliced_nodes = set(art_sliced_graph.nx_graph.nodes)
                # Identify import nodes(need to lift them out)
                art_import_node = import_nodes.union(
                    set(
                        [
                            _node
                            for _node in art_sliced_nodes
                            if len(self.node_context[_node]["module_import"])
                            > 0
                        ]
                    )
                )
                # Ancestors of import node should be also for import
                art_import_node_ancestors = set(
                    itertools.chain.from_iterable(
                        [
                            self.graph.get_ancestors(import_node_id)
                            for import_node_id in art_import_node
                        ]
                    )
                )
                # All nodes related to import modules
                import_nodes = import_nodes.union(
                    (
                        art_import_node.union(art_import_node_ancestors)
                    ).intersection(art_sliced_nodes)
                    - used_nodes
                )

                # Nodes only belong to this artifact
                artifact_context["node_list"] = (
                    art_sliced_nodes - used_nodes - import_nodes
                )

                # Update used nodes for next iteration
                used_nodes = used_nodes.union(
                    artifact_context["node_list"]
                ).union(import_nodes)

                artifact_context = {
                    **artifact_context,
                    **self._get_variable_information(
                        artifact_context["node_list"]
                    ),
                }

                # Update node context to label the node is assigned to this artifact
                for n_id in artifact_context["node_list"]:
                    self.node_context[n_id]["artifact_name"] = n[
                        "assigned_artifact"
                    ]

                for n_id in import_nodes:
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
                    - import_nodes
                )

                artifact_context["predecessor_artifact"] = set(
                    [
                        self.node_context[n_id]["artifact_name"]
                        for n_id in artifact_context["predecessor_nodes"]
                    ]
                )

                # Get information about which input variable is originated from which artifact
                artifact_context["input_variable_sources"] = dict()
                for prev_id in artifact_context["predecessor_nodes"]:
                    predecessor_variables = (
                        self.node_context[prev_id]["assigned_variables"]
                        if len(
                            self.node_context[prev_id]["assigned_variables"]
                        )
                        > 0
                        else self.node_context[prev_id][
                            # "dependent_variables"
                            "tracked_variables"
                        ]
                    )
                    predecessor_artifact = self.node_context[prev_id][
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
                        common_nodes = art_sliced_nodes.intersection(
                            set(source_art_slice_variable_graph.nx_graph.nodes)
                        )

                        # Split one artifact_context into two
                        if len(common_nodes) > 0:
                            common_artifact_variables = (
                                self._get_variable_information(common_nodes)
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
                                self._get_variable_information(remaining_nodes)
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
                list(import_nodes)
            ),
            segment_type=GraphSegmentType.IMPORT,
            all_variables=set(),
            input_variables=set(),
            return_variables=[],
        )

        # print(self.input_parameters_node)
        self.input_parameters_segment = GraphSegment(
            artifact_name="",
            graph_segment=self._get_subgraph_from_node_list(
                list(self.input_parameters_node.values())
            ),
            segment_type=GraphSegmentType.INPUT_PARAMETERS,
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
        Generate a module definition for artifacts within the session.

        This includes all functions that create artifacts and common variables.
        It will also include a pipeline function that executes artifact creating
        function in topologically sorted order.
        """

        indentation_block = " " * indentation

        import_block = self.import_segment.get_import_block(indentation=0)

        input_parameters_block = (
            self.input_parameters_segment.get_input_parameters_block()
        )

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

def pipeline({input_parameters_block}):
{calculation_codeblock}
{indentation_block}return {return_string}

if __name__=="__main__":
{indentation_block}pipeline()
"""
        else:
            module_definition_string = f"""import copy
{import_block}{function_definitions}

def pipeline({input_parameters_block}):
{indentation_block}sessionartifacts = []
{calculation_codeblock}
{indentation_block}return sessionartifacts

if __name__=="__main__":
{indentation_block}pipeline()
"""

        return module_definition_string

    def get_session_module(self, keep_lineapy_save: bool = False):
        import importlib.util
        import sys
        from importlib.abc import Loader

        module_name = f"session_{self.session_id.replace('-','_')}"
        with open(f"/tmp/{module_name}.py", "w") as f:
            f.writelines(
                self.get_session_module_definition(
                    keep_lineapy_save=keep_lineapy_save
                )
            )
        spec = importlib.util.spec_from_file_location(
            module_name, f"/tmp/{module_name}.py"
        )
        if spec is not None:
            session_module = importlib.util.module_from_spec(spec)
            assert isinstance(spec.loader, Loader)
            sys.modules["module.name"] = session_module
            spec.loader.exec_module(session_module)
            return session_module

        return
