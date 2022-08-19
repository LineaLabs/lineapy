import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from lineapy.api.api_classes import LineaArtifact
from lineapy.data.graph import Graph
from lineapy.data.types import CallNode, GlobalNode, LineaID, MutateNode, Node
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.node_collection import (
    NodeCollection,
    NodeCollectionType,
    NodeInfo,
)
from lineapy.graph_reader.program_slice import get_slice_graph
from lineapy.graph_reader.utils import _is_import_node
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


@dataclass
class SessionArtifacts:
    """
    Refactor a given session graph for use in a downstream task (e.g., pipeline building).
    """

    session_id: LineaID
    graph: Graph
    db: RelationalLineaDB
    nx_graph: nx.DiGraph
    artifact_nodecollections: List[NodeCollection]
    import_nodecollection: NodeCollection
    artifact_list: List[LineaArtifact]
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
        self.artifact_nodecollections = []
        self.node_context = OrderedDict()
        self.input_parameters = input_parameters

        self._update_node_context()
        self._slice_session_artifacts()

    def _update_dependent_variables(
        self, nodeinfo: NodeInfo, variable_dict: Dict[LineaID, Set[str]]
    ) -> None:
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

    def _update_tracked_variables(
        self, nodeinfo: NodeInfo, node_id: LineaID
    ) -> None:
        # Determine the tracked variables of each node
        # Fix me when you see return variables in refactor behaves strange
        node = self.graph.get_node(node_id=node_id)
        if len(nodeinfo.assigned_variables) > 0:
            nodeinfo.tracked_variables = nodeinfo.assigned_variables
        elif isinstance(node, MutateNode) or isinstance(node, GlobalNode):
            predecessor_call_id = node.call_id
            if predecessor_call_id in nodeinfo.predecessors:
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
        import_dict: Dict[LineaID, Set[str]] = OrderedDict()
        self.input_parameters_node = dict()
        for node_id, variable_name in self.db.get_variables_for_session(
            self.session_id
        ):
            if _is_import_node(self.graph, node_id):
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
                        logger.error(
                            "Variable %s, is defined more than once", var
                        )
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

            self._update_dependent_variables(nodeinfo, variable_dict)
            self._update_tracked_variables(nodeinfo, node_id)

            self.node_context[node_id] = nodeinfo

        for var, node_id in self.input_parameters_node.items():
            if len(self.node_context[node_id].dependent_variables) > 0:
                # Duplicated variable name existing
                logger.error(
                    "LineaPy only suppor literal value as input parameters for now."
                )
                raise Exception

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

    def _get_sliced_nodes(
        self, node_id: LineaID
    ) -> Tuple[Set[LineaID], Set[LineaID]]:
        nodes = set(get_slice_graph(self.graph, [node_id]).nx_graph.nodes)

        importnodes = set(
            [
                _node
                for _node in nodes
                if len(self.node_context[_node].module_import) > 0
            ]
        )
        # Ancestors of import node should be also for import
        importnodes = importnodes.union(
            *[
                self.graph.get_ancestors(import_node_id)
                for import_node_id in importnodes
            ]
        )
        # Ancestors might not in nodes
        importnodes = importnodes.intersection(nodes)
        return nodes, importnodes

    def _get_predecessor_info(self, nodes, importnodes):
        # Figure out where each predecessor is coming from which artifact
        predecessor_nodes = set().union(
            *[self.node_context[n_id].predecessors for n_id in nodes]
        )
        predecessor_nodes = predecessor_nodes - nodes - importnodes
        predecessor_artifact = set(
            self.node_context[n_id].artifact_name for n_id in predecessor_nodes
        )
        return predecessor_nodes, predecessor_artifact

    def _get_input_variable_sources(self, pred_nodes) -> Dict[str, Set[str]]:
        # Get information about which input variable is originated from which artifact
        input_variable_sources: Dict[str, Set[str]] = dict()
        for pred_id in pred_nodes:
            pred_variables = (
                self.node_context[pred_id].assigned_variables
                if len(self.node_context[pred_id].assigned_variables) > 0
                else self.node_context[pred_id].tracked_variables
            )
            pred_art = self.node_context[pred_id].artifact_name
            assert isinstance(pred_art, str)
            if pred_art != "module_import":
                input_variable_sources[pred_art] = input_variable_sources.get(
                    pred_art, set()
                ).union(pred_variables)
        return input_variable_sources

    def _get_common_variables(
        self, curr_nc: NodeCollection, pred_nc: NodeCollection
    ) -> Tuple[List[str], Set[LineaID]]:
        assert isinstance(pred_nc.name, str)
        common_inner_variables = (
            pred_nc.all_variables - set(pred_nc.return_variables)
        ).intersection(curr_nc.input_variable_sources[pred_nc.name])

        common_nodes = set()
        if len(common_inner_variables) > 0:
            slice_variable_nodes = [
                n
                for n in curr_nc.predecessor_nodes
                if n in pred_nc.node_list
                and self.node_context[n].assigned_artifact
                != self.node_context[n].artifact_name
            ]
            assert pred_nc.graph_segment is not None
            source_art_slice_variable_graph = get_slice_graph(
                pred_nc.graph_segment, slice_variable_nodes
            )
            common_nodes = set(source_art_slice_variable_graph.nx_graph.nodes)
        else:
            common_nodes = set()

        # Want the return variales in consistent ordering
        return sorted(list(common_inner_variables)), common_nodes

    def _slice_session_artifacts(self) -> None:
        self.used_nodes: Set[LineaID] = set()  # Track nodes that get ever used
        self.import_nodes: Set[LineaID] = set()
        self.artifact_nodecollections = list()
        for node_id, n in self.node_context.items():
            if n.assigned_artifact is not None and node_id in [
                art._node_id for art in self.artifact_list
            ]:
                sliced_nodes, sliced_import_nodes = self._get_sliced_nodes(
                    node_id
                )
                self.import_nodes.update(sliced_import_nodes - self.used_nodes)
                art_nodes = sliced_nodes - self.used_nodes - self.import_nodes
                self.used_nodes = self.used_nodes.union(art_nodes).union(
                    self.import_nodes
                )
                pred_nodes, pred_artifact = self._get_predecessor_info(
                    art_nodes, self.import_nodes
                )
                input_variable_sources = self._get_input_variable_sources(
                    pred_nodes
                )

                nodecollectioninfo = NodeCollection(
                    collection_type=NodeCollectionType.ARTIFACT,
                    artifact_node_id=node_id,
                    name=n.assigned_artifact,
                    tracked_variables=n.tracked_variables,
                    return_variables=list(n.tracked_variables),
                    node_list=art_nodes,
                    predecessor_nodes=pred_nodes,
                    predecessor_artifact=pred_artifact,
                    input_variable_sources=input_variable_sources,
                    sliced_nodes=sliced_nodes,
                )

                # Update node context to label the node is assigned to this artifact
                for n_id in nodecollectioninfo.node_list:
                    self.node_context[n_id].artifact_name = n.assigned_artifact
                for n_id in self.import_nodes:
                    self.node_context[n_id].artifact_name = "module_import"

                # Check whether we need to breakdown existing artifact node
                # collection. If the precedent node in precedent collection
                # is not the artifact itself, this means we should split the
                # existing collection.
                for (
                    source_artifact_name,
                    variables,
                ) in input_variable_sources.items():
                    source_id, source_info = [
                        (i, context)
                        for i, context in enumerate(
                            self.artifact_nodecollections
                        )
                        if context.name == source_artifact_name
                    ][0]

                    # Common variables between two artifacts
                    (
                        common_inner_variables,
                        common_nodes,
                    ) = self._get_common_variables(
                        nodecollectioninfo, source_info
                    )

                    if len(common_inner_variables) > 0 and len(common_nodes):

                        common_nodecollectioninfo = NodeCollection(
                            collection_type=NodeCollectionType.COMMON_VARIABLE,
                            name=f"{'_'.join(common_inner_variables)}_for_artifact_{source_info.name}_and_downstream",
                            return_variables=common_inner_variables,
                            node_list=common_nodes,
                        )
                        common_nodecollectioninfo._update_variable_info(
                            self.node_context, self.input_parameters_node
                        )
                        common_nodecollectioninfo._update_graph(self.graph)

                        remaining_nodes = source_info.node_list - common_nodes
                        remaining_nodecollectioninfo = NodeCollection(
                            collection_type=NodeCollectionType.ARTIFACT,
                            name=source_info.name,
                            return_variables=source_info.return_variables,
                            node_list=remaining_nodes,
                        )
                        remaining_nodecollectioninfo._update_variable_info(
                            self.node_context, self.input_parameters_node
                        )
                        remaining_nodecollectioninfo._update_graph(self.graph)

                        self.artifact_nodecollections = (
                            self.artifact_nodecollections[:source_id]
                            + [
                                common_nodecollectioninfo,
                                remaining_nodecollectioninfo,
                            ]
                            + self.artifact_nodecollections[(source_id + 1) :]
                        )

                # Remove input parameter node
                nodecollectioninfo.node_list = (
                    nodecollectioninfo.node_list
                    - set(self.input_parameters_node.values())
                )
                nodecollectioninfo._update_variable_info(
                    self.node_context, self.input_parameters_node
                )
                nodecollectioninfo._update_graph(self.graph)
                self.artifact_nodecollections.append(nodecollectioninfo)

        # NodeCollection for import
        self.import_nodecollection = NodeCollection(
            collection_type=NodeCollectionType.IMPORT,
            node_list=self.import_nodes,
        )
        self.import_nodecollection._update_graph(self.graph)

        # NodeCollection for input parameters
        self.input_parameters_nodecollection = NodeCollection(
            collection_type=NodeCollectionType.INPUT_PARAMETERS,
            node_list=set(self.input_parameters_node.values()),
        )
        self.input_parameters_nodecollection._update_variable_info(
            self.node_context, self.input_parameters_node
        )
        self.input_parameters_nodecollection._update_graph(self.graph)

    def _get_first_artifact_name(self) -> Optional[str]:
        for coll in self.artifact_nodecollections:
            if coll.collection_type == NodeCollectionType.ARTIFACT:
                return coll.safename
        return None
