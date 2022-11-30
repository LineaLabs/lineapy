import logging
from dataclasses import dataclass
from itertools import chain
from typing import Dict, List

import networkx as nx
from networkx.exception import NetworkXUnfeasible

from lineapy.api.models.linea_artifact import LineaArtifact, LineaArtifactDef
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.graph_reader.utils import (
    check_duplicates,
    get_artifacts_grouped_by_session,
    get_db_artifacts_from_artifactdef,
)
from lineapy.plugins.task import TaskGraphEdge
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
        ] = get_db_artifacts_from_artifactdef(self.db, target_artifacts)

        # Retrieve reuse precomputed artifact objects
        self.pre_computed_artifacts: List[
            LineaArtifact
        ] = get_db_artifacts_from_artifactdef(
            self.db, reuse_pre_computed_artifacts
        )

        # ------ Group artifacts by session using SessionArtifact ------
        # For each session, construct SessionArtifacts object
        self.session_artifacts: Dict[LineaID, SessionArtifacts] = {}
        for (
            session_id,
            target_artifacts_by_session,
        ) in get_artifacts_grouped_by_session(self.target_artifacts):

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

    def validate_dependencies(self, dependencies: TaskGraphEdge = {}):
        """
        Validate provided dependencies.

        This function checks if all the artifacts defined in dependencies can be found in
        this artifact collection and if the dependencies creates any circular dependencies.
        """
        # Merge task graph from all sessions
        combined_taskgraph = nx.union_all(
            [
                session_artifact.nodecollection_dependencies.graph
                for _, session_artifact in self.session_artifacts.items()
            ]
        )

        # Add edge for user specified dependencies
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
        combined_taskgraph.add_edges_from(task_dependency_edges)

        # Check for unused dependencies and throw error
        task_dependency_nodes = set(chain(*task_dependency_edges))
        unused_artname = [
            artname
            for artname in task_dependency_nodes
            if artname not in list(combined_taskgraph.nodes)
        ]
        if len(unused_artname) > 0:
            msg = (
                "Dependency graph includes artifacts"
                + ", ".join(unused_artname)
                + ", which are not in this artifact collection: "
                + ", ".join(list(combined_taskgraph.nodes))
            )
            raise KeyError(msg)

        # Check if the graph is acyclic
        if nx.is_directed_acyclic_graph(combined_taskgraph) is False:
            raise Exception(
                "LineaPy detected conflict with the provided dependencies. "
                "Please check if the provided dependencies include circular relationships."
            )

    def create_inter_session_taskgraph(self, dependencies: TaskGraphEdge = {}):
        # Helper dictionary to look up artifact information by name
        art_name_to_session_id: Dict[str, LineaID] = {}
        for artifact in self.target_artifacts:
            art_name_to_session_id[artifact.name] = artifact._session_id
            art_name_to_session_id[
                slugify(artifact.name)
            ] = artifact._session_id

        session_id_nodes = list(self.session_artifacts.keys())
        session_id_edges = list(
            chain.from_iterable(
                (
                    (
                        art_name_to_session_id[slugify(from_artname)],
                        art_name_to_session_id[slugify(to_artname)],
                    )
                    for from_artname in from_artname_set
                )
                for to_artname, from_artname_set in dependencies.items()
            )
        )
        # remove loops in graph for dependencies within a session
        session_id_edges = [
            edge for edge in session_id_edges if edge[0] != edge[1]
        ]
        inter_session_graph = nx.DiGraph()
        inter_session_graph.add_nodes_from(session_id_nodes)
        inter_session_graph.add_edges_from(session_id_edges)
        return inter_session_graph

    def sort_session_artifacts(
        self, dependencies: TaskGraphEdge = {}
    ) -> List[SessionArtifacts]:
        """
        Use the user-provided artifact dependencies to
        topologically sort a list of SessionArtifacts objects.
        Raise an exception if the graph contains a cycle.

        NOTE: Current implementation of LineaPy demands it be able to
        linearly order different sessions, which prohibits any
        circular dependencies between sessions, e.g.,
        Artifact A (Session 1) -> Artifact B (Session 2) -> Artifact C (Session 1).
        We need to implement inter-session graph merge if we want to
        support such circular dependencies between sessions,
        which is a future project.
        """
        # Construct inter session dependency graph
        if dependencies:
            self.validate_dependencies(dependencies)

        inter_session_taskgraph = self.create_inter_session_taskgraph(
            dependencies
        )
        # Sort the session_id
        try:
            session_id_sorted = list(
                nx.topological_sort(inter_session_taskgraph)
            )
        except NetworkXUnfeasible:
            raise Exception(
                "Current implementation of LineaPy demands it be able to linearly order different sessions, "
                "which prohibits any circular dependencies between sessions. "
                "Please check if your provided dependencies include such circular dependencies between sessions, "
                "e.g., Artifact A (Session 1) -> Artifact B (Session 2) -> Artifact C (Session 1)."
            )

        return [
            self.session_artifacts[session_id]
            for session_id in session_id_sorted
        ]
