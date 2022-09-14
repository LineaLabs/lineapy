import logging
from collections import Counter, OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from lineapy.api.models.linea_artifact import LineaArtifact
from lineapy.data.graph import Graph
from lineapy.data.types import CallNode, GlobalNode, LineaID, MutateNode, Node
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.node_collection import (
    NodeCollection,
    NodeCollectionType,
    NodeInfo,
)
from lineapy.graph_reader.program_slice import get_slice_graph
from lineapy.graph_reader.types import InputVariable
from lineapy.graph_reader.utils import _is_import_node
from lineapy.plugins.task import TaskGraph
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


@dataclass
class SessionArtifacts:
    """
    Refactor a given session graph for use in a downstream task (e.g., pipeline building).
    """

    _session_id: LineaID
    graph: Graph
    db: RelationalLineaDB
    artifact_nodecollections: List[NodeCollection]
    import_nodecollection: NodeCollection
    input_parameters_node: Dict[str, LineaID]
    node_context: Dict[LineaID, NodeInfo]
    target_artifacts: List[LineaArtifact]
    reuse_pre_computed_artifacts: Dict[str, LineaArtifact]
    all_session_artifacts: Dict[LineaID, LineaArtifact]
    input_parameters: List[str]
    nodecollection_dependencies: TaskGraph

    def __init__(
        self,
        db: RelationalLineaDB,
        target_artifacts: List[LineaArtifact],
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: Dict[str, LineaArtifact] = {},
    ) -> None:
        self.db = db
        self.target_artifacts = target_artifacts
        self.target_artifacts_name = [
            art.name for art in self.target_artifacts
        ]
        self._session_id = self.target_artifacts[0]._session_id
        self._session_graph = Graph.create_session_graph(
            self.db, self._session_id
        )
        # Only interested union of sliced graph of each artifacts
        self.graph = self._get_subgraph_from_node_list(
            list(
                set.union(
                    *[
                        set(art._get_subgraph().nx_graph.nodes)
                        for art in target_artifacts
                    ]
                )
            )
        )
        self.artifact_nodecollections = []
        self.node_context = OrderedDict()
        self.input_parameters = input_parameters
        self.reuse_pre_computed_artifacts = reuse_pre_computed_artifacts

        # Retrive all artifacts within the subgraph of target artifacts
        self._retrive_all_session_artifacts()
        # Add extra attributes(from predecessors) at session Liena nodes
        self._update_node_context()
        # Divide session graph into a set of non-overlapping NodeCollection
        self._slice_session_artifacts()
        # Determine dependencies of NodeCollections and check whether to
        # replace it with pre-calculated value from artifact store
        self._update_nodecollection_dependencies()

    @property
    def session_id(self) -> LineaID:
        return self._session_id

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

    def _retrive_all_session_artifacts(self):
        """
        Retrive all artifacts(targeted, reused) within the session.
        Note that, the version of reused artifacts within the session does not
        need to be the same as in `reuse_pre_computed_artifacts`; thus, we need
        to retrive the correct version in the session with the correct node id
        to enable graph manipulation.
        """
        # Map node id to artifact assignment within the session
        self.all_session_artifacts = {}
        for artifact in self.db.get_artifacts_for_session(self._session_id):
            if (
                artifact.name in self.target_artifacts_name
                or artifact.name in self.reuse_pre_computed_artifacts.keys()
            ):
                assert isinstance(artifact.name, str)
                self.all_session_artifacts[
                    artifact.node_id
                ] = LineaArtifact.get_artifact_from_name_and_version(
                    self.db, artifact.name, artifact.version
                )

        # Check only one artifact in the session with the name within reuse_pre_computed_artifacts
        pre_computed_artifacts_name_count = Counter(
            [art.name for nodeid, art in self.all_session_artifacts.items()]
        )
        for art_name, ct in pre_computed_artifacts_name_count.items():
            if ct > 1:
                raise ValueError(
                    f"More than one artifacts with the same name {art_name} in the session."
                    + "Please remove it from reuse_pre_computed_artifacts."
                )

    def _update_node_context(self):
        """
        Traverse every node within the session in topologically sorted order
        and update node_context with following informations

        assigned_variables : variables assigned at this node
        assigned_artifact : this node is pointing to some artifact
        predecessors : predecessors of the node
        dependent_variables : union of if any variable is assigned at
            predecessor node, use the assigned variables; otherwise, use the
            dependent_variables
        tracked_variables : variables that this node is point to
        module_import : module name/alias that this node is point to

        Note that, it is possible to add all these new attributes during the
        Linea graph creating phase. However, this might scrifice the runtime
        performance since some of the information need to query the attributes
        from predecessors.
        """
        # Map each variable node ID to the corresponding variable name(when variable assigned)
        # Need to treat import different from regular variable assignment
        variable_dict: Dict[LineaID, Set[str]] = OrderedDict()
        import_dict: Dict[LineaID, Set[str]] = OrderedDict()
        self.input_parameters_node = dict()

        input_parameters_assignment_nodes: Dict[str, List[LineaID]] = dict()
        for node_id, variable_name in self.db.get_variables_for_session(
            self._session_id
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
                    input_parameters_assignment_nodes[
                        var
                    ] = input_parameters_assignment_nodes.get(var, []) + [
                        node_id
                    ]

        # Identify variable dependencies of each node in topological order
        for node_id in nx.topological_sort(self.graph.nx_graph):

            nodeinfo = NodeInfo(
                assigned_variables=variable_dict.get(node_id, set()),
                assigned_artifact=self.all_session_artifacts[node_id].name
                if node_id in self.all_session_artifacts.keys()
                else None,
                dependent_variables=set(),
                predecessors=set(self.graph.nx_graph.predecessors(node_id)),
                tracked_variables=set(),
                module_import=import_dict.get(node_id, set()),
            )

            self._update_dependent_variables(nodeinfo, variable_dict)
            self._update_tracked_variables(nodeinfo, node_id)

            self.node_context[node_id] = nodeinfo

        # If a variable is declared as an input parameters, we only support
        # the literal assignment only happen once in the entire session at this
        # moment. If there is a way to specify which literal assignment to use
        # as an input parameter. We can relax this restriction.
        for var, node_ids in input_parameters_assignment_nodes.items():
            for node_id in node_ids:
                is_literal_assignment = (
                    len(self.node_context[node_id].dependent_variables) == 0
                )
                has_assigned_before = (
                    self.input_parameters_node.get(var, None) is not None
                )
                if is_literal_assignment:
                    if has_assigned_before:
                        raise ValueError(
                            "Variable %s, is defined more than once", var
                        )
                    else:
                        self.input_parameters_node[var] = node_id

        for var, node_id in self.input_parameters_node.items():
            if len(self.node_context[node_id].dependent_variables) > 0:
                # Duplicated variable name existing
                logger.error(
                    "LineaPy only supports literal value as input parameters for now."
                )
                raise Exception

    def _get_subgraph_from_node_list(self, node_list: List[LineaID]) -> Graph:
        """
        Return the subgraph as LineaPy Graph from list of node id
        """
        nodes: List[Node] = []
        for node_id in node_list:
            node = self._session_graph.get_node(node_id)
            if node is not None:
                nodes.append(node)

        return self._session_graph.get_subgraph(nodes)

    def _get_sliced_nodes(
        self, node_id: LineaID
    ) -> Tuple[Set[LineaID], Set[LineaID]]:
        """
        Get sliced nodes from session graph and separate nodes for import
        and main calculation.
        """
        nodes = set(get_slice_graph(self.graph, [node_id]).nx_graph.nodes)
        # Identify import nodes
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
        """
        Figure out where each predecessor is coming from which artifact in
        both artifact name and nodeid
        """
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
        """
        Identify common variables for two NodeCollections.
        """
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
        """
        Divide all session nodes into a set of non-overlapping nodes. Each set
        responds to one artifact or common variables calculation. All the import
        nodes will belong to one set and all input variable nodes will belong to
        another set.
        """
        self.used_nodes: Set[LineaID] = set()  # Track nodes that get ever used
        self.import_nodes: Set[LineaID] = set()
        self.artifact_nodecollections = list()
        for node_id, n in self.node_context.items():
            if (
                n.assigned_artifact is not None
                and node_id in self.all_session_artifacts.keys()
            ):
                art = self.all_session_artifacts[node_id]
                # Identify nodes to calculate the artifact from sliced graphs
                sliced_nodes, sliced_import_nodes = self._get_sliced_nodes(
                    node_id
                )
                # Attach import nodes to import NodeCollection
                self.import_nodes.update(sliced_import_nodes - self.used_nodes)
                # New nodes to calculate this specifict artifact
                art_nodes = sliced_nodes - self.used_nodes - self.import_nodes
                # Update used nodes
                self.used_nodes = self.used_nodes.union(art_nodes).union(
                    self.import_nodes
                )
                # Identify precedent artifacts(id and name)
                pred_nodes, pred_artifact = self._get_predecessor_info(
                    art_nodes, self.import_nodes
                )
                # Identify input variables are coming from which artifacts
                input_variable_sources = self._get_input_variable_sources(
                    pred_nodes
                )
                # Check whether this artifact should be replaced by
                # pre-computed value, None if no and (name, version) if yes
                matched_pre_computed = (
                    (
                        n.assigned_artifact,
                        self.reuse_pre_computed_artifacts[
                            n.assigned_artifact
                        ].version,
                    )
                    if n.assigned_artifact
                    in self.reuse_pre_computed_artifacts.keys()
                    else None
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
                    pre_computed_artifact=matched_pre_computed,
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

                    # If common inner variables detected, split the precedent
                    # NodeCollection into two parts. One for calculation of
                    # common variables and the other for rest of artifact
                    # calculation.
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
                            pre_computed_artifact=source_info.pre_computed_artifact,
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

    def _update_nodecollection_dependencies(self):
        """
        Identify the dependencies graph of each NodeCollections that compute
        an artifact or common variables for multiple artifacts. Remove useless
        NodeCollections that only use to calculate artifacts in
        reuse_pre_computed_artifacts list.
        """
        last_appearance_nc: Dict[str, str] = dict()
        dependencies: Dict[str, Set[str]] = dict()
        # Artifact nodes that are going to be replaced by cached value
        cache_nodes = [
            nc.name
            for nc in self.artifact_nodecollections
            if nc.pre_computed_artifact is not None
        ]
        # Determine input variables of a nodecollection are coming from output
        # variables of nodecollections to build the NodeCollection dependencies
        for nc in self.artifact_nodecollections:
            dependencies[nc.name] = set()
            for var in nc.input_variables:
                if var in last_appearance_nc.keys():
                    dependencies[nc.name].add(last_appearance_nc[var])
            for var in nc.return_variables:
                last_appearance_nc[var] = nc.name
        # Nodecollection dependencies
        self.nodecollection_dependencies = TaskGraph(
            nodes=[nc.name for nc in self.artifact_nodecollections],
            mapping={
                nc.name: nc.safename for nc in self.artifact_nodecollections
            },
            edges=dependencies,
        )
        # Graph with each nodecollection as node
        nc_graph = self.nodecollection_dependencies.graph
        # Edges point to cached nodes
        cache_nodes_edges = [
            (from_node, to_node)
            for from_node, to_node in nc_graph.edges
            if from_node in cache_nodes
        ]
        # Remove these edges and the nodecollection graph might split into
        # multiple components, only keep components with user required artifact
        nc_graph.remove_nodes_from(cache_nodes)
        if nc_graph is not None and len(cache_nodes) > 0:
            artifact_names = set([art.name for art in self.target_artifacts])

            nc_graph = nx.union_all(
                [
                    nc_graph.subgraph(c).copy()
                    for c in nx.connected_components(nc_graph.to_undirected())
                    if len(set(c).intersection(artifact_names)) > 0
                ]
            )
            nc_graph.add_nodes_from(cache_nodes)
            nc_graph.add_edges_from(
                [edge for edge in cache_nodes_edges if edge[1] in nc_graph]
            )
            self.artifact_nodecollections = [
                art
                for art in self.artifact_nodecollections
                if art.name in nc_graph.nodes
            ]

    def _get_first_artifact_name(self) -> Optional[str]:
        """
        Return the name of first artifact(topologically sorted)
        """
        for coll in self.artifact_nodecollections:
            if coll.collection_type == NodeCollectionType.ARTIFACT:
                return coll.safename
        return None

    def get_session_module_imports(self, indentation=0) -> str:
        """
        Return all the import statement for the session
        """
        return self.import_nodecollection.get_import_block(
            indentation=indentation
        )

    def get_session_function_name(self) -> str:
        """
        Return the session function name: run_session_including_{first_artifact_name}
        """
        first_artifact_name = self._get_first_artifact_name()
        if first_artifact_name is not None:
            return f"run_session_including_{first_artifact_name}"
        return ""

    def get_session_function_body(
        self, indentation, return_dict_name="artifacts"
    ) -> str:
        """
        Return the args for the session function
        """
        return "\n".join(
            [
                coll.get_function_call_block(
                    indentation=indentation,
                    keep_lineapy_save=False,
                    result_placeholder=None
                    if coll.collection_type != NodeCollectionType.ARTIFACT
                    else return_dict_name,
                )
                for coll in self.artifact_nodecollections
            ]
        )

    def get_session_input_parameters_lines(self, indentation=4) -> str:
        """
        Return lines of session code that are replaced by user selected input
        parameters. These lines also serve as the default values of these
        variables.
        """
        return self.input_parameters_nodecollection.get_input_parameters_block(
            indentation=indentation
        )

    def get_session_input_parameters_spec(self) -> Dict[str, InputVariable]:
        """ """
        session_input_variables: Dict[str, InputVariable] = dict()
        for line in self.get_session_input_parameters_lines().split("\n"):
            variable_def = line.strip(" ").rstrip(",")
            if len(variable_def) > 0:
                variable_name = variable_def.split("=")[0].strip(" ")
                value = eval(variable_def.split("=")[1].strip(" "))
                value_type = type(value)
                if ":" in variable_name:
                    variable_name = variable_def.split(":")[0]
                    typing_info = variable_def.split(":")[1]
                    session_input_variables[variable_name] = InputVariable(
                        variable_name=variable_name,
                        value=value,
                        typing_info=typing_info,
                        value_type=value_type,
                    )
                else:
                    session_input_variables[variable_name] = InputVariable(
                        variable_name=variable_name,
                        value=value,
                        value_type=value_type,
                    )
        return session_input_variables

    def get_session_function_callblock(self) -> str:
        """
        Return the code to make the call to the session function as
        `session_function_name(input_parameters)`
        """
        session_function_name = self.get_session_function_name()
        if session_function_name != "":
            session_input_parameters = ", ".join(
                self.get_session_input_parameters_spec().keys()
            )
            return f"{session_function_name}({session_input_parameters})"
        else:
            return ""

    def get_session_artifact_function_definitions(
        self, indentation=4
    ) -> List[str]:
        """
        Return the definition of each targeted artifacts calculation
        functions
        """
        return [
            coll.get_function_definition(indentation=indentation)
            for coll in self.artifact_nodecollections
        ]

    def get_session_function(
        self, indentation=4, return_dict_name="artifacts"
    ) -> str:
        """
        Return the definition of the session function that executes the
        calculation of all targeted artifacts.
        """
        indentation_block = " " * indentation
        SESSION_FUNCTION_TEMPLATE = load_plugin_template(
            "session_function.jinja"
        )
        session_function = SESSION_FUNCTION_TEMPLATE.render(
            session_input_parameters_body=self.get_session_input_parameters_lines(),
            indentation_block=indentation_block,
            session_function_name=self.get_session_function_name(),
            session_function_body=self.get_session_function_body(
                indentation=indentation
            ),
            return_dict_name=return_dict_name,
        )
        return session_function
