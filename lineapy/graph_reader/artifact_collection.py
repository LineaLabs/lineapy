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
from typing import Dict, List, Tuple, Union

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
from lineapy.plugins.utils import load_plugin_template
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
        target_artifacts: Union[
            List[str], List[Tuple[str, int]], List[Union[str, Tuple[str, int]]]
        ],
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: Union[
            List[str], List[Tuple[str, int]], List[Union[str, Tuple[str, int]]]
        ] = [],  # type: ignore
    ) -> None:
        self.db: RelationalLineaDB = db
        self.session_artifacts: Dict[LineaID, SessionArtifacts] = {}
        self.artifact_session: Dict[str, LineaID] = {}
        self.art_name_to_node_id: Dict[str, LineaID] = {}
        self.node_id_to_session_id: Dict[LineaID, LineaID] = {}
        self.input_parameters = input_parameters
        if len(input_parameters) != len(set(input_parameters)):
            raise ValueError(
                f"Duplicated input parameters detected in {input_parameters}"
            )
        artifacts_by_session: Dict[LineaID, List[LineaArtifact]] = defaultdict(
            list
        )
        # Retrieve artifact objects and group them by session ID
        for art_entry in target_artifacts:
            art_def = get_lineaartifactdef(art_entry=art_entry)
            # Check no two target artifacts could have the same name
            # Otherwise will have name collision.
            if art_def["artifact_name"] in self.art_name_to_node_id.keys():
                logger.error("%s is duplicated in ", art_def["artifact_name"])
                raise KeyError("%s is duplicated", art_def["artifact_name"])
            # Retrieve artifact
            art = LineaArtifact.get_artifact_from_def(self.db, art_def)
            self.art_name_to_node_id[art_def["artifact_name"]] = art._node_id
            self.node_id_to_session_id[art._node_id] = art._session_id
            # Put artifact in the right session group
            artifacts_by_session[art._session_id].append(art)
            # Record session_id of an artifact
            self.artifact_session[art.name] = art._session_id
            self.artifact_session[art.name.replace(" ", "_")] = art._session_id

        pre_calculated_artifacts: Dict[str, LineaArtifact] = {}
        for art_entry in reuse_pre_computed_artifacts:
            art_def = get_lineaartifactdef(art_entry=art_entry)
            # Check no two reuse pre-computed artifacts could have the same name
            # Otherwise will confuse which one to use
            if art_def["artifact_name"] in pre_calculated_artifacts.keys():
                msg = (
                    "Duplicated reuse_pre_computed_artifacts names detected in "
                    + f"{list(pre_calculated_artifacts.keys())}"
                )
                logger.error(msg)
                raise KeyError(msg)
            # Retrieve artifact
            art = LineaArtifact.get_artifact_from_def(self.db, art_def)
            pre_calculated_artifacts[art.name] = art

        # For each session, construct SessionArtifacts object
        for session_id, session_artifacts in artifacts_by_session.items():
            self.session_artifacts[session_id] = SessionArtifacts(
                self.db,
                session_artifacts,
                input_parameters=input_parameters,
                reuse_pre_computed_artifacts=pre_calculated_artifacts,
            )

        # Check all reuse_pre_computed artifacts is used
        all_sessions_artifacts = []
        for sa in self.session_artifacts.values():
            all_sessions_artifacts += [
                art.name for art in sa.all_session_artifacts.values()
            ]
        for reuse_art in pre_calculated_artifacts.values():
            reuse_name = reuse_art.name
            if reuse_name not in all_sessions_artifacts:
                msg = (
                    f"Artifact {reuse_name} cannot be reused since it is not "
                    + "used to calulate artifacts "
                    + f"{', '.join(self.artifact_session.keys())}. "
                    + "Try to remove it from the reuse list."
                )
                raise KeyError(msg)

    def _sort_session_artifacts(
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

        # Merge task graph from all sessions
        combined_taskgraph = nx.union_all(
            [
                sa.nodecollection_dependencies.graph
                for session_id, sa in self.session_artifacts.items()
            ]
        )
        # Add edge for user specified dependencies
        task_dependency_edges = list(
            chain.from_iterable(
                (
                    (artname.replace(" ", "_"), to_artname.replace(" ", "_"))
                    for artname in from_artname
                )
                for to_artname, from_artname in dependencies.items()
            )
        )
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
        combined_taskgraph.add_edges_from(task_dependency_edges)
        # Check if the graph is acyclic
        if nx.is_directed_acyclic_graph(combined_taskgraph) is False:
            raise Exception(
                "LineaPy detected conflict with the provided dependencies. "
                "Please check if the provided dependencies include circular relationships."
            )

        # Construct inter session dependency graph
        session_id_nodes = list(self.session_artifacts.keys())
        session_id_edges = [
            (self.artifact_session[n1], self.artifact_session[n2])
            for n1, n2 in task_dependency_edges
            if self.artifact_session[n1] != self.artifact_session[n2]
        ]
        inter_session_graph = nx.DiGraph()
        inter_session_graph.add_nodes_from(session_id_nodes)
        inter_session_graph.add_edges_from(session_id_edges)
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
                + f"The following parameters are missing {missing_parameters}."
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
        session_artifacts_sorted = self._sort_session_artifacts(
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
