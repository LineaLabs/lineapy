import logging
from dataclasses import dataclass
from itertools import chain
from typing import Dict, List

import networkx as nx

from lineapy.api.models.linea_artifact import LineaArtifact, LineaArtifactDef
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.graph_reader.utils import (
    check_duplicates,
    get_artifacts_from_artifactdef,
    group_artifacts_by_session,
)
from lineapy.plugins.task import TaskGraph, TaskGraphEdge, slugify_dependencies
from lineapy.plugins.utils import slugify
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


@dataclass
class ArtifactCollection:
    """
    `ArtifactCollection` can be thought of as a box where the inserted group of artifacts and
    their graph(s) get refactored into reusable components (i.e., functions with non-overlapping
    operations). With this modularization, it can then support various downstream code generation
    tasks such as pipeline file writing.

    For now, `ArtifactCollection` is meant to be kept and used as an abstraction/tool for internal
    dev use only. That is, the class and its methods will NOT be exposed directly to the user.
    Instead, it is intended to be used by/in/for other user-facing APIs.
    """

    def __init__(
        self,
        db: RelationalLineaDB,
        target_artifacts: List[LineaArtifactDef],
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: List[LineaArtifactDef] = [],
        dependencies: TaskGraphEdge = {},
    ) -> None:
        self.db: RelationalLineaDB = db

        self.input_parameters = input_parameters

        # ------ Validate inputs ------
        # check if any duplicates exist in input parameters
        if len(input_parameters) != len(set(input_parameters)):
            raise ValueError(
                f"Duplicated input parameters detected in {input_parameters}"
            )
        # Check if target artifacts name has been repeated in the input list
        check_duplicates(target_artifacts)
        # Check if entries in reuse pre computed artifacts list have been repeated
        check_duplicates(reuse_pre_computed_artifacts)

        # ------ Initialize Linea Artifacts from artifactdef ------
        # Retrieve target artifact objects
        self.target_artifacts: List[
            LineaArtifact
        ] = get_artifacts_from_artifactdef(self.db, target_artifacts)

        # Retrieve reuse precomputed artifact objects
        self.pre_computed_artifacts: List[
            LineaArtifact
        ] = get_artifacts_from_artifactdef(
            self.db, reuse_pre_computed_artifacts
        )

        # ------ Group artifacts by session using SessionArtifact ------
        # For each session, construct SessionArtifacts object
        self.session_artifacts: Dict[LineaID, SessionArtifacts] = {}
        for (
            session_id,
            target_artifacts_by_session,
        ) in group_artifacts_by_session(self.target_artifacts):

            self.session_artifacts[session_id] = SessionArtifacts(
                self.db,
                target_artifacts_by_session,
                input_parameters=input_parameters,
                # TODO: LIN-653, LIN-640 only collect matched pre_computed artifacts in this Session
                # instead of grabbing all Artifacts as currently required by SessionArtifact
                reuse_pre_computed_artifacts=self.pre_computed_artifacts,
            )

        # TODO: LIN-653, LIN-640
        # Add some type of validation that all re-use compute artifacts can be matched to
        # a target artifact before the creation of SessionArtifacts.
        # If calls to .values() are repeated in the class, it might indicate a need for a new datastructure to hold the values
        all_sessions_artifacts = [
            art.name
            for sa in self.session_artifacts.values()
            for art in sa.all_session_artifacts.values()
        ]

        # Check all reuse_pre_computed artifacts is used
        for reuse_art in self.pre_computed_artifacts:
            reuse_name = reuse_art.name
            if reuse_name not in all_sessions_artifacts:
                msg = (
                    f"Artifact {reuse_name} cannot be reused since it is not "
                    + "used to calculate artifacts "
                    + f"{', '.join([str(art) for art in target_artifacts])}. "
                    + "Try to remove it from the reuse list."
                )
                raise KeyError(msg)

        # slugify dependencies and save to self.dependencies
        self.dependencies: TaskGraphEdge = slugify_dependencies(dependencies)

        # Create taskgraph breakdowns based on dependencies
        self.inter_session_taskgraph = self._create_inter_session_taskgraph(
            self.dependencies
        )

        self.inter_artifact_taskgraph = self._create_inter_artifact_taskgraph(
            self.dependencies
        )

    def _validate_dependencies_used(
        self, taskgraph: TaskGraph, dependencies: TaskGraphEdge
    ):
        """
        Validate all the provided dependencies can be used in the taskgraph.

        This function checks if all the artifacts defined in dependencies can be found in
        this artifact collection. Raises an error if not all dependencies are usable.
        """

        # Check for unused dependencies and throw error
        task_dependency_nodes = set(chain(dependencies))
        unused_artname = [
            artname
            for artname in task_dependency_nodes
            if artname not in list(taskgraph.graph.nodes)
        ]
        if len(unused_artname) > 0:
            msg = (
                "Dependency graph includes artifacts "
                + ", ".join(unused_artname)
                + ", which are not in this artifact collection: "
                + ", ".join(list(taskgraph.graph.nodes))
            )
            raise KeyError(msg)

    def _validate_graph_acyclic(self, taskgraph: TaskGraph):
        """
        Validate provided dependencies created an acyclic TaskGraph.
        """
        if nx.is_directed_acyclic_graph(taskgraph.graph) is False:
            raise Exception(
                "LineaPy detected conflict with the provided dependencies. "
                "Please check if the provided dependencies include circular relationships."
            )

    def _create_inter_session_taskgraph(
        self, dependencies: TaskGraphEdge
    ) -> TaskGraph:
        """
        Returns TaskGraph for dependencies between Sessions.

        Nodes are SessionIds and edges between Sessions are specified by the dependencies
        existing in the combined_taskgraph.
        """

        inter_session_taskgraph = TaskGraph(nodes=[], edges={})

        # Helper dictionary to look up the session for each task
        task_name_to_session_id: Dict[str, str] = {}

        # add subgraph for each session_artifact
        for sa in self.session_artifacts.values():
            inter_session_taskgraph.graph = nx.compose(
                inter_session_taskgraph.graph,
                sa.nodecollection_dependencies.graph,
            )
            for node_coll_task in sa.nodecollection_dependencies.graph.nodes:
                task_name_to_session_id[node_coll_task] = str(sa.session_id)

        task_dependency_edges = list(
            chain.from_iterable(
                (
                    (
                        slugify(from_artname),
                        slugify(to_artname),
                    )
                    for from_artname in from_artname_set
                )
                for to_artname, from_artname_set in dependencies.items()
            )
        )

        self._validate_dependencies_used(inter_session_taskgraph, dependencies)

        inter_session_taskgraph.graph.add_edges_from(task_dependency_edges)

        inter_session_taskgraph = inter_session_taskgraph.remap_nodes(
            task_name_to_session_id
        )

        # remove loops in graph for dependencies within a session
        inter_session_taskgraph.remove_self_loops()
        self._validate_graph_acyclic(inter_session_taskgraph)

        return inter_session_taskgraph

    def _create_inter_artifact_taskgraph(
        self, dependencies: TaskGraphEdge
    ) -> TaskGraph:
        """
        Returns TaskGraph for dependencies between "Artifacts".

        Nodes correspond to nodecollections.

        Edges between artifacts in different sessions are replaced
        so that all the dependencies pointing to the target artifact instead point to
        its "root" tasks in the session which are source tasks that can be used to generate the artifact.

        Session 1: A -> B
        Session 2: C -> D

        If a user specifies a dependency from B -> D, the inter artifact taskgraph will
        instead draw a dependency from B -> C to ensure B runs before all the intra session
        dependencies of D.

        Note: These additional edges prevent bugs as the user maybe be unable to specify dependencies
        to automatically generated components.
        """
        inter_artifact_taskgraph = TaskGraph(nodes=[], edges={})

        # add subgraph for each session_artifact
        for sa in self.session_artifacts.values():
            inter_artifact_taskgraph.graph = nx.compose(
                inter_artifact_taskgraph.graph,
                sa.nodecollection_dependencies.graph,
            )

        art_name_to_session_id: Dict[str, str] = {}
        for artifact in self.target_artifacts:
            art_name_to_session_id[slugify(artifact.name)] = str(
                artifact._session_id
            )

        self._validate_dependencies_used(
            inter_artifact_taskgraph, dependencies
        )

        for to_artname, from_artname_set in dependencies.items():
            for from_artname in from_artname_set:
                from_session_id, to_session_id = (
                    art_name_to_session_id[from_artname],
                    art_name_to_session_id[to_artname],
                )

                if from_session_id != to_session_id:
                    # this edge needs to be replaced, all the dependencies of target artifact in the same session
                    # must be run after the source artifact is created

                    to_graph = self.session_artifacts[
                        LineaID(to_session_id)
                    ].nodecollection_dependencies

                    to_art_ancestors = nx.ancestors(
                        to_graph.graph, source=to_artname
                    )

                    for to_source_node in to_graph.source_nodes:
                        if to_source_node in to_art_ancestors:
                            inter_artifact_taskgraph.graph.add_edge(
                                from_artname, to_source_node
                            )
                else:
                    # when user specifies intra-session dependency, we can ignore since
                    # we assume Linea has all the intra-session dependencies figured out.
                    pass

        self._validate_graph_acyclic(inter_artifact_taskgraph)
        return inter_artifact_taskgraph

    def sort_session_artifacts(
        self,
    ) -> List[SessionArtifacts]:
        """
        Use the user-provided artifact dependencies to
        topologically sort a list of SessionArtifacts objects.
        Raise an exception if the graph contains a cycle.

        ??? note

            Current implementation of LineaPy demands it be able to
            linearly order different sessions, which prohibits any
            circular dependencies between sessions, e.g.,
            Artifact A (Session 1) -> Artifact B (Session 2) -> Artifact C (Session 1).
            We need to implement inter-session graph merge if we want to
            support such circular dependencies between sessions,
            which is a future project.
        """
        # Sort the session_id
        session_id_sorted = self.inter_session_taskgraph.get_taskorder()

        return [
            self.session_artifacts[LineaID(session_id)]
            for session_id in session_id_sorted
        ]
