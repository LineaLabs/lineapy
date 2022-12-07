import itertools
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
from lineapy.plugins.task import TaskGraph, TaskGraphEdge
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

        self.dependencies = dependencies
        self._validate_dependencies()
        self.inter_session_taskgraph = self.create_inter_session_taskgraph()
        self.inter_artifact_taskgraph = self.create_inter_artifact_taskgraph()

    def _validate_dependencies(self):
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
                for to_artname, from_artname_set in self.dependencies.items()
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

    def create_inter_session_taskgraph(self) -> TaskGraph:
        # todo slugify
        inter_session_graph = TaskGraph(
            nodes=[art.name for art in self.target_artifacts],
            edges=self.dependencies,
        )

        # Helper dictionary to look up artifact information by name
        art_name_to_session_id: Dict[str, str] = {}
        for artifact in self.target_artifacts:
            art_name_to_session_id[artifact.name] = str(artifact._session_id)
            art_name_to_session_id[slugify(artifact.name)] = str(
                artifact._session_id
            )

        print(inter_session_graph)
        inter_session_graph.remap_nodes(art_name_to_session_id)
        print(inter_session_graph)

        # remove loops in graph for dependencies within a session
        inter_session_graph.remove_self_loops()

        return inter_session_graph

    def create_inter_artifact_taskgraph(self) -> TaskGraph:

        inter_artifact_taskgraph = TaskGraph(nodes=[], edges={})

        # add subgraph for each session_artifact
        for sa in self.session_artifacts.values():
            inter_artifact_taskgraph.graph = nx.compose(
                inter_artifact_taskgraph.graph,
                sa.nodecollection_dependencies.graph,
            )

        for (
            from_session_id,
            to_session_id,
        ) in self.inter_session_taskgraph.graph.edges:
            # get sink nodes from the first session artifact
            from_session_sink_nodes = self.session_artifacts[
                from_session_id
            ].nodecollection_dependencies.sink_nodes

            # get source nodes from the second session artifact
            to_session_source_nodes = self.session_artifacts[
                to_session_id
            ].nodecollection_dependencies.source_nodes

            # add edges between each pair of sink/sources

            inter_artifact_taskgraph.graph.add_edges_from(
                itertools.product(
                    from_session_sink_nodes, to_session_source_nodes
                )
            )
        return inter_artifact_taskgraph

    def sort_session_artifacts(
        self,
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
        # Sort the session_id
        session_id_sorted = self.inter_session_taskgraph.get_taskorder()

        return [
            self.session_artifacts[LineaID(session_id)]
            for session_id in session_id_sorted
        ]
