import logging
from collections import Counter, OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, cast

import networkx as nx

from lineapy.api.models.linea_artifact import (
    LineaArtifact,
    get_lineaartifactdef,
)
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    GlobalNode,
    LineaID,
    LiteralNode,
    MutateNode,
    Node,
)
from lineapy.db.db import RelationalLineaDB
from lineapy.db.relational import ImportNodeORM
from lineapy.graph_reader.node_collection import (
    ArtifactNodeCollection,
    ImportNodeCollection,
    InputVarNodeCollection,
    NodeInfo,
    UserCodeNodeCollection,
)
from lineapy.graph_reader.program_slice import get_slice_graph
from lineapy.graph_reader.utils import is_import_node
from lineapy.plugins.task import TaskGraph
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
    session_graph: Graph
    db: RelationalLineaDB
    usercode_nodecollections: List[UserCodeNodeCollection]
    import_nodecollection: ImportNodeCollection
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
        reuse_pre_computed_artifacts: List[LineaArtifact] = [],
    ) -> None:
        self.db = db
        self.target_artifacts = target_artifacts
        self.target_artifacts_name = [
            art.name for art in self.target_artifacts
        ]
        self._session_id = self.target_artifacts[0]._session_id
        self.session_graph = Graph.create_session_graph(
            self.db, self._session_id
        )

        def _get_subgraph_from_node_list(
            session_graph: Graph, node_list: List[LineaID]
        ) -> Graph:
            """
            Return the subgraph as LineaPy Graph from list of node id
            """
            nodes: List[Node] = []
            for node_id in node_list:
                node = session_graph.get_node(node_id)
                if node is not None:
                    nodes.append(node)

            return self.session_graph.get_subgraph(nodes)

        # Only interested union of sliced graph of each artifacts
        self.graph = _get_subgraph_from_node_list(
            self.session_graph,
            list(
                set.union(
                    *[
                        set(art._get_subgraph().nx_graph.nodes)
                        for art in target_artifacts
                    ]
                )
            ),
        )
        self.usercode_nodecollections = []
        self.node_context = OrderedDict()
        self.input_parameters = input_parameters
        self.reuse_pre_computed_artifacts = {
            art.name: art for art in reuse_pre_computed_artifacts
        }

        # Retrive all artifacts within the subgraph of target artifacts
        self._retrive_all_session_artifacts()
        # Add extra attributes(from predecessors) at session Linea nodes
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
        session_artifacts_name_count = Counter(
            [art.name for nodeid, art in self.all_session_artifacts.items()]
        )
        for art_name in self.reuse_pre_computed_artifacts.keys():
            if session_artifacts_name_count[art_name] > 1:
                raise ValueError(
                    f"More than one artifacts with the same name {art_name} in the session."
                    + "Please remove it from reuse_pre_computed_artifacts."
                )

    def _update_node_context(self):
        """
        Traverse every node within the session in topologically sorted order
        and update node_context with following information.

        - assigned_variables : variables assigned at this node
        - assigned_artifact : this node is pointing to some artifact
        - predecessors : predecessors of the node
        - dependent_variables : union of if any variable is assigned at
            predecessor node, use the assigned variables; otherwise, use the
            dependent_variables
        - tracked_variables : variables that this node is point to
        - module_import : module name/alias that this node is point to

        Note that, it is possible to add all these new attributes during the
        Linea graph creating phase. However, this might sacrifice the runtime
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
            if is_import_node(self.graph, node_id):
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
        # We allow multiple assignments to non-literals to handle common cases like the
        # following:
        # x = 1
        # x = x + 1
        # input_parameters = [x]
        # In this case, the original definition of x = 1 will be parametrized.
        for var, node_ids in input_parameters_assignment_nodes.items():
            for node_id in node_ids:
                if node_id in self.node_context.keys():
                    is_literal_assignment = (
                        len(self.node_context[node_id].dependent_variables)
                        == 0
                    )
                    previous_assignment = self.input_parameters_node.get(
                        var, None
                    )

                    if previous_assignment is None:
                        self.input_parameters_node[var] = node_id
                    else:
                        previous_assignment_is_literal = (
                            len(
                                self.node_context[
                                    previous_assignment
                                ].dependent_variables
                            )
                            == 0
                        )

                        if (
                            is_literal_assignment
                            and previous_assignment_is_literal
                        ):
                            raise ValueError(
                                f"Variable {var}, is defined more than once"
                            )
                        elif not previous_assignment_is_literal:
                            # previous assignment is not literal, so we can reassign it
                            self.input_parameters_node[var] = node_id
                        # else previous assignment is literal and we should not override it

        for var, node_id in self.input_parameters_node.items():
            if len(self.node_context[node_id].dependent_variables) > 0:
                dep_vars = ", ".join(
                    sorted(
                        list(self.node_context[node_id].dependent_variables)
                    )
                )
                raise ValueError(
                    f"LineaPy only supports input parameters without dependent variables for now. "
                    f"{var} has dependent variables: {dep_vars}."
                )

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

    def _get_common_variables(
        self, curr_nc: UserCodeNodeCollection, pred_nc: UserCodeNodeCollection
    ) -> Tuple[List[str], Set[LineaID]]:
        """
        Identify common variables for two NodeCollections.
        """
        assert isinstance(pred_nc.name, str)
        common_inner_variables = (
            pred_nc.all_variables - set(pred_nc.return_variables)
        ).intersection(
            curr_nc.get_input_variable_sources(self.node_context)[pred_nc.name]
        )

        common_nodes = set()
        if len(common_inner_variables) > 0:
            slice_variable_nodes = [
                n
                for n in curr_nc.predecessor_nodes
                if n in pred_nc.node_list
                and self.node_context[n].assigned_artifact
                != self.node_context[n].artifact_name
            ]
            pred_graph_segment = self.graph.get_subgraph_from_id(
                list(pred_nc.node_list)
            )
            assert pred_graph_segment is not None
            source_art_slice_variable_graph = get_slice_graph(
                pred_graph_segment,
                slice_variable_nodes,
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
        self.usercode_nodecollections = list()
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
                pred_nodes, _ = self._get_predecessor_info(
                    art_nodes, self.import_nodes
                )
                # Check whether this artifact should be replaced by
                # pre-computed value, None if no and (name, version) if yes
                if (
                    n.assigned_artifact
                    in self.reuse_pre_computed_artifacts.keys()
                ):
                    reuse_def = get_lineaartifactdef(
                        (
                            n.assigned_artifact,
                            self.reuse_pre_computed_artifacts[
                                n.assigned_artifact
                            ].version,
                        )
                    )

                    nodecollectioninfo: ArtifactNodeCollection = (
                        ArtifactNodeCollection(
                            name=n.assigned_artifact,
                            node_list=art_nodes,
                            tracked_variables=n.tracked_variables,
                            return_variables=list(n.tracked_variables),
                            predecessor_nodes=pred_nodes,
                            is_pre_computed=True,
                            pre_computed_artifact=reuse_def,
                        )
                    )
                else:
                    nodecollectioninfo = ArtifactNodeCollection(
                        name=n.assigned_artifact,
                        node_list=art_nodes,
                        tracked_variables=n.tracked_variables,
                        return_variables=list(n.tracked_variables),
                        predecessor_nodes=pred_nodes,
                        is_pre_computed=False,
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
                ) in nodecollectioninfo.get_input_variable_sources(
                    self.node_context
                ).items():
                    source_id, source_info = [
                        (i, context)
                        for i, context in enumerate(
                            self.usercode_nodecollections
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

                        common_nodecollectioninfo = UserCodeNodeCollection(
                            name=f"{'_'.join(common_inner_variables)}_for_artifact_{source_info.name}_and_downstream",
                            node_list=common_nodes,
                            return_variables=common_inner_variables,
                        )
                        common_nodecollectioninfo.update_variable_info(
                            self.node_context, self.input_parameters_node
                        )

                        remaining_nodes = source_info.node_list - common_nodes
                        if isinstance(source_info, ArtifactNodeCollection):
                            remaining_nodecollectioninfo: UserCodeNodeCollection = ArtifactNodeCollection(
                                name=source_info.name,
                                node_list=remaining_nodes,
                                return_variables=source_info.return_variables,
                                is_pre_computed=source_info.is_pre_computed,
                                pre_computed_artifact=source_info.pre_computed_artifact,
                            )
                        else:  # outputs a common variable, use base UserCodeNodeCollection instead.
                            remaining_nodecollectioninfo = UserCodeNodeCollection(
                                name=source_info.name,
                                node_list=remaining_nodes,
                                return_variables=source_info.return_variables,
                            )

                        remaining_nodecollectioninfo.update_variable_info(
                            self.node_context, self.input_parameters_node
                        )

                        self.usercode_nodecollections = (
                            self.usercode_nodecollections[:source_id]
                            + [
                                common_nodecollectioninfo,
                                remaining_nodecollectioninfo,
                            ]
                            + self.usercode_nodecollections[(source_id + 1) :]
                        )

                # Remove input parameter node
                nodecollectioninfo.update_variable_info(
                    self.node_context, self.input_parameters_node
                )
                nodecollectioninfo.node_list = (
                    nodecollectioninfo.node_list
                    - set(self.input_parameters_node.values())
                )
                self.usercode_nodecollections.append(nodecollectioninfo)

        # NodeCollection for import
        self.import_nodecollection = ImportNodeCollection(
            name="", node_list=self.import_nodes
        )

        # NodeCollection for input parameters
        self.input_parameters_nodecollection = InputVarNodeCollection(
            name="",
            node_list=set(self.input_parameters_node.values()),
        )

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
            for nc in self.usercode_nodecollections
            if isinstance(nc, ArtifactNodeCollection) and nc.is_pre_computed
        ]
        # Determine input variables of a nodecollection are coming from output
        # variables of nodecollections to build the NodeCollection dependencies
        for nc in self.usercode_nodecollections:
            dependencies[nc.name] = set()
            for var in nc.input_variables:
                if var in last_appearance_nc.keys():
                    dependencies[nc.name].add(last_appearance_nc[var])
            for var in nc.return_variables:
                last_appearance_nc[var] = nc.name
        # Nodecollection dependencies
        self.nodecollection_dependencies = TaskGraph(
            nodes=[nc.name for nc in self.usercode_nodecollections],
            edges=dependencies,
        )

        self.nodecollection_dependencies = (
            self.nodecollection_dependencies.remap_nodes(
                mapping={
                    nc.name: nc.safename
                    for nc in self.usercode_nodecollections
                },
            )
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
            self.usercode_nodecollections = [
                art
                for art in self.usercode_nodecollections
                if art.name in nc_graph.nodes
            ]
            self.nodecollection_dependencies.graph = nc_graph

    def _get_first_artifact_name(self) -> Optional[str]:
        """
        Return the name of first artifact(topologically sorted).
        """
        for coll in self.usercode_nodecollections:
            if isinstance(coll, ArtifactNodeCollection):
                return coll.safename
        return None

    def get_libraries(self) -> List[ImportNodeORM]:
        """
        Return a list of ImportNodeORM's containing the libraries associated with this SessionArtifact.

        This function works by taking the imported library information from the whole session
        and checking if the library is used for this SessionArtifact by trying to match with the
        relevant nodes in the Session Artifacts import_nodes attribute.

        Specifically we look for CallNodes with function `l_import` and a single argument.
        The value of the argument Literal node will contain the base library name we want because
        CallNodes with a single argument are the ones importing without the base_module optional argument,
        which is only the case when we are importing the base library which we want the name of.
        """

        # All libraries in a session
        session_libs = self.db.get_libraries_for_session(self.session_id)

        # Libraries this SessionArtifact uses will be stored here by name
        session_artifact_lib_names: Set[str] = set()

        # Get all nodes in SessionArtifact "import_nodes" attribute.
        # Note that these nodes are not actually ImportNodes, but simply the
        # Call/Literal/Lookup Nodes associated with the captured lines
        # that are import statements.
        import_nodes = {
            id: self.db.get_node_by_id(id) for id in self.import_nodes
        }

        # Try to find library names through their associated CallNode.
        # This Node must call l_import with one argument which will be the
        # base library name we're interested in.
        for node_id, node in import_nodes.items():

            # check if node is CallNode doing module import
            if is_import_node(self.graph, node_id):
                node = cast(CallNode, node)

                # Check function has a single argument
                if len(node.positional_args) != 1:
                    continue

                # This single argument should be a literal node holding the library name
                argument_node = import_nodes[node.positional_args[0].id]
                if not isinstance(argument_node, LiteralNode):
                    continue

                session_artifact_lib_names.add(argument_node.value)

        # Get only session libraries that are used in this SessionArtifact
        session_artifact_libs = [
            lib_info
            for lib_info in session_libs
            if lib_info.package_name in session_artifact_lib_names
        ]

        return session_artifact_libs
