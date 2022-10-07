import importlib.util
import itertools
import logging
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from importlib.abc import Loader
from itertools import chain
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

import networkx as nx
from networkx.exception import NetworkXUnfeasible

from lineapy.api.models.linea_artifact import (
    LineaArtifact,
    get_lineaartifactdef,
)
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.graph_reader.types import InputVariable
from lineapy.plugins.task import TaskGraphEdge
from lineapy.plugins.utils import load_plugin_template, slugify
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

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
        target_artifacts: List[Union[str, Tuple[str, int]]],
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]] = [],
    ) -> None:
        self.db: RelationalLineaDB = db

        self.input_parameters = input_parameters
        if len(input_parameters) != len(set(input_parameters)):
            raise ValueError(
                f"Duplicated input parameters detected in {input_parameters}"
            )

        # Retrieve target artifact objects and group them by session ID
        self.target_artifacts_by_session = (
            self._get_artifacts_grouped_by_session(target_artifacts)
        )

        # Retrieve reuse precomputed artifact objects and group them by session ID
        self.pre_computed_artifacts_by_session = (
            self._get_artifacts_grouped_by_session(
                reuse_pre_computed_artifacts
            )
        )

        # TODO: LIN-653, LIN-640
        # Add some type of validation that all re-use compute artifacts can be matched to
        # a target artifact.

        # For each session, construct SessionArtifacts object
        self.session_artifacts: Dict[LineaID, SessionArtifacts] = {}
        for (
            session_id,
            session_artifacts,
        ) in self.target_artifacts_by_session.items():
            # TODO: LIN-653, LIN-640 only collect matched pre_computed artifacts in this Session
            # instead of grabbing all Artifacts as currently required by SessionArtifact
            pre_calculated_artifacts = sum(
                self.pre_computed_artifacts_by_session.values(), []
            )

            self.session_artifacts[session_id] = SessionArtifacts(
                self.db,
                session_artifacts,
                input_parameters=input_parameters,
                reuse_pre_computed_artifacts=pre_calculated_artifacts,
            )

    def _get_artifacts_grouped_by_session(
        self, artifact_entries: List[Union[str, Tuple[str, int]]]
    ) -> Dict[LineaID, List[LineaArtifact]]:
        """
        Get LineaArtifact from each artifact entry and group by the Session they belong to.

        Artifact entries are specified as name and optionally version as the end user would specify.

        This helper function is used to group target and reuse_precomputed artifacts so that we can
        create SessionArtifacts for each Session.
        """
        artifacts_grouped_by_session: Dict[
            LineaID, List[LineaArtifact]
        ] = defaultdict(list)
        seen_artifact_names: Set[str] = set()
        for art_entry in artifact_entries:
            art_def = get_lineaartifactdef(art_entry=art_entry)
            # Check no two target artifacts have the same name
            if art_def["artifact_name"] in seen_artifact_names:
                raise KeyError(
                    "Artifact %s is duplicated", art_def["artifact_name"]
                )
            # Retrieve artifact and put it in the right group
            art = LineaArtifact.get_artifact_from_def(self.db, art_def)
            artifacts_grouped_by_session[art._session_id].append(art)
            seen_artifact_names.add(art_def["artifact_name"])

        return artifacts_grouped_by_session

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

    def create_inter_session_graph(self, dependencies: TaskGraphEdge = {}):
        # Helper dictionary to look up artifact information by name
        art_name_to_session_id: Dict[str, LineaID] = {}
        for (
            session_id,
            artifact_list,
        ) in self.target_artifacts_by_session.items():
            for artifact in artifact_list:
                art_name_to_session_id[artifact.name] = session_id
                art_name_to_session_id[slugify(artifact.name)] = session_id

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

        inter_session_graph = self.create_inter_session_graph(dependencies)
        # Sort the session_id
        try:
            session_id_sorted = list(nx.topological_sort(inter_session_graph))
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

    # TODO: Move to writers
    def _compose_module(
        self,
        session_artifacts_sorted: List[SessionArtifacts],
        indentation: int = 4,
        return_dict_name="artifacts",
    ) -> str:
        """
        Generate a Python module that calculates artifacts
        in the given artifact collection.
        """
        indentation_block = " " * indentation

        module_imports = "\n".join(
            [
                sa.get_session_module_imports()
                for sa in session_artifacts_sorted
            ]
        )

        artifact_function_definition = "\n".join(
            list(
                itertools.chain.from_iterable(
                    [
                        sa.get_session_artifact_function_definitions(
                            indentation=indentation
                        )
                        for sa in session_artifacts_sorted
                    ]
                )
            )
        )

        session_functions = "\n".join(
            [
                sa.get_session_function(indentation=indentation)
                for sa in session_artifacts_sorted
            ]
        )

        module_function_body = "\n".join(
            [
                f"{indentation_block}{return_dict_name}.update({sa.get_session_function_callblock()})"
                for sa in session_artifacts_sorted
            ]
        )

        module_input_parameters: List[InputVariable] = []
        for sa in session_artifacts_sorted:
            module_input_parameters += list(
                sa.get_session_input_parameters_spec().values()
            )

        module_input_parameters_list = [
            param.variable_name for param in module_input_parameters
        ]
        if len(module_input_parameters_list) != len(
            set(module_input_parameters_list)
        ):
            raise ValueError(
                f"Duplicated input parameters {module_input_parameters_list} across multiple sessions"
            )
        elif set(module_input_parameters_list) != set(self.input_parameters):
            missing_parameters = set(self.input_parameters) - set(
                module_input_parameters_list
            )
            raise ValueError(
                f"Detected input parameters {module_input_parameters_list} do not agree with user input {self.input_parameters}. "
                + f"The following variables do not have references in any session code: {missing_parameters}."
            )

        # Sort input parameter for the run_all in the module as the same order
        # of user's input parameter
        user_input_parameters_ordering = {
            var: i for i, var in enumerate(self.input_parameters)
        }
        module_input_parameters.sort(
            key=lambda x: user_input_parameters_ordering[x.variable_name]
        )

        # Put all together to generate module text
        MODULE_TEMPLATE = load_plugin_template("module.jinja")
        module_text = MODULE_TEMPLATE.render(
            indentation_block=indentation_block,
            module_imports=module_imports,
            artifact_functions=artifact_function_definition,
            session_functions=session_functions,
            module_function_body=module_function_body,
            default_input_parameters=[
                param.default_args for param in module_input_parameters
            ],
            parser_input_parameters=[
                param.parser_args for param in module_input_parameters
            ],
            parser_blocks=[
                param.parser_body for param in module_input_parameters
            ],
        )

        return module_text

    # TODO: Move to writers
    def generate_module_text(
        self,
        dependencies: TaskGraphEdge = {},
        indentation: int = 4,
    ) -> str:
        """
        Generate a Python module that reproduces artifacts in the artifact collection.
        This module is meant to provide function components that can be easily reused to
        incorporate artifacts into other code contexts.

        :param dependencies: Dependency between artifacts, expressed in graphlib format.
            For instance, ``{"B": {"A", "C"}}`` means artifacts A and C are prerequisites for artifact B.
        """
        # Sort sessions topologically (applicable if artifacts come from multiple sessions)
        session_artifacts_sorted = self.sort_session_artifacts(
            dependencies=dependencies
        )

        # Generate module text
        module_text = self._compose_module(
            session_artifacts_sorted=session_artifacts_sorted,
            indentation=indentation,
        )
        return prettify(module_text)

    def get_module(self, dependencies: TaskGraphEdge = {}):
        """
        Writing module text to a temp file and load module with names of
        ``session_art1_art2_...```
        """

        module_name = f"session_{'_'.join(self.session_artifacts.keys())}"
        temp_folder = tempfile.mkdtemp()
        temp_module_path = Path(temp_folder, f"{module_name}.py")
        with open(temp_module_path, "w") as f:
            f.writelines(self.generate_module_text(dependencies=dependencies))

        spec = importlib.util.spec_from_file_location(
            module_name, temp_module_path
        )
        if spec is not None:
            session_module = importlib.util.module_from_spec(spec)
            assert isinstance(spec.loader, Loader)
            sys.modules["module.name"] = session_module
            spec.loader.exec_module(session_module)
            return session_module
        else:
            raise Exception("LineaPy cannot retrive a module.")
