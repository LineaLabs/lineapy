import importlib.util
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
from lineapy.graph_reader.node_collection import NodeCollectionType
from lineapy.graph_reader.session_artifacts import SessionArtifacts
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
        reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]] = [],
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

    @staticmethod
    def _extract_session_module(
        session_artifacts: SessionArtifacts,
        indentation: int = 4,
    ) -> dict:
        """
        Utility to extract relevant module components from the given SessionArtifacts.
        To be used for composing the multi-session module.
        """
        indentation_block = " " * indentation

        # Generate import statement block for the given session
        session_imports = (
            session_artifacts.import_nodecollection.get_import_block(
                indentation=0
            )
        )

        # Generate function definition for each session artifact
        artifact_functions = "\n".join(
            [
                coll.get_function_definition(indentation=indentation)
                for coll in session_artifacts.artifact_nodecollections
            ]
        )

        # Generate session function name
        first_art_name = session_artifacts._get_first_artifact_name()
        assert first_art_name is not None
        session_function_name = f"run_session_including_{first_art_name}"

        # Generate session function body
        return_dict_name = "artifacts"  # List for capturing artifacts before irrelevant downstream mutation
        session_function_body = "\n".join(
            [
                coll.get_function_call_block(
                    indentation=indentation,
                    keep_lineapy_save=False,
                    result_placeholder=None
                    if coll.collection_type != NodeCollectionType.ARTIFACT
                    else return_dict_name,
                )
                for coll in session_artifacts.artifact_nodecollections
            ]
        )

        # Generate session function return value string
        session_function_return = ", ".join(
            [
                coll.return_variables[0]
                for coll in session_artifacts.artifact_nodecollections
                if coll.collection_type == NodeCollectionType.ARTIFACT
            ]
        )

        session_input_parameters_body = session_artifacts.input_parameters_nodecollection.get_input_parameters_block(
            indentation=indentation
        )

        SESSION_FUNCTION_TEMPLATE = load_plugin_template(
            "session_function.jinja"
        )
        session_function = SESSION_FUNCTION_TEMPLATE.render(
            session_input_parameters_body=session_input_parameters_body,
            indentation_block=indentation_block,
            session_function_name=session_function_name,
            session_function_body=session_function_body,
            return_dict_name=return_dict_name,
        )

        session_input_parameters = ", ".join(
            session_artifacts.input_parameters_node.keys()
        )

        # Generate calculation code block for the session
        # This is to be used in multi-session module
        session_calculation = f"{indentation_block}artifacts.update({session_function_name}({session_input_parameters}))"

        return {
            "session_imports": session_imports,
            "artifact_functions": artifact_functions,
            "session_function": session_function,
            "session_function_return": session_function_return,
            "session_calculation": session_calculation,
            "session_input_parameters_body": session_input_parameters_body,
        }

    def _compose_module(
        self,
        session_artifacts_sorted: List[SessionArtifacts],
        indentation: int = 4,
    ) -> str:
        """
        Generate a Python module that calculates artifacts
        in the given artifact collection.
        """
        indentation_block = " " * indentation

        # Extract module script components by session
        session_modules = [
            self._extract_session_module(
                session_artifacts=session_artifacts,
                indentation=indentation,
            )
            for session_artifacts in session_artifacts_sorted
        ]

        # Combine components by "type"
        module_imports = "\n".join(
            [module["session_imports"] for module in session_modules]
        )
        artifact_functions = "\n".join(
            [module["artifact_functions"] for module in session_modules]
        )
        session_functions = "\n".join(
            [module["session_function"] for module in session_modules]
        )
        module_function_body = "\n".join(
            [module["session_calculation"] for module in session_modules]
        )
        module_function_return = ", ".join(
            [module["session_function_return"] for module in session_modules]
        )

        input_parameters_body = []
        for module in session_modules:
            input_parameters_body += [
                line.lstrip(" ").rstrip(",")
                for line in module["session_input_parameters_body"].split("\n")
                if len(line.lstrip(" ").rstrip(",")) > 0
            ]

        module_input_parameters_body = (
            ",".join(input_parameters_body)
            if len(input_parameters_body) <= 1
            else "\n"
            + f",\n{indentation_block}".join(input_parameters_body)
            + ",\n"
        )

        module_input_parameters_list = [
            x.split("=")[0].strip(" ") for x in input_parameters_body
        ]
        if len(module_input_parameters_list) != len(
            set(module_input_parameters_list)
        ):
            raise ValueError(
                f"Duplicated input parameters {module_input_parameters_list} across multiple sessions"
            )
        elif set(module_input_parameters_list) != set(self.input_parameters):
            raise ValueError(
                f"Detected input parameters {module_input_parameters_list} do not agree with user input {self.input_parameters}"
            )

        # Put all together to generate module text
        MODULE_TEMPLATE = load_plugin_template("module.jinja")
        module_text = MODULE_TEMPLATE.render(
            indentation_block=indentation_block,
            module_imports=module_imports,
            artifact_functions=artifact_functions,
            session_functions=session_functions,
            module_function_body=module_function_body,
            module_function_return=module_function_return,
            module_input_parameters=module_input_parameters_body,
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
