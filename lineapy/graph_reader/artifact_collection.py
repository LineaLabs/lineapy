import importlib.util
import logging
import sys
import tempfile
from dataclasses import dataclass
from importlib.abc import Loader
from itertools import chain
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import networkx as nx
from networkx.exception import NetworkXUnfeasible
from typing_extensions import NotRequired, TypedDict

from lineapy.api.api_classes import LineaArtifact
from lineapy.data.types import LineaID
from lineapy.graph_reader.node_collection import NodeCollectionType
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.plugins.task import TaskGraphEdge
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class ArtifactDef(TypedDict):
    artifact_name: str
    version: NotRequired[Optional[int]]


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
        artifacts: List[Union[str, Tuple[str, int]]],
        input_parameters: List[str] = [],
    ) -> None:
        from lineapy.api.api import get

        self.session_artifacts: Dict[LineaID, SessionArtifacts] = {}
        self.art_name_to_node_id: Dict[str, LineaID] = {}
        self.node_id_to_session_id: Dict[LineaID, LineaID] = {}
        self.input_parameters = input_parameters
        if len(input_parameters) != len(set(input_parameters)):
            raise ValueError(
                f"Duplicated input parameters detected in {input_parameters}"
            )

        artifacts_by_session: Dict[LineaID, List[LineaArtifact]] = {}

        # Retrieve artifact objects and group them by session ID
        for art_entry in artifacts:
            # Construct args for artifact retrieval
            args: ArtifactDef
            if isinstance(art_entry, str):
                args = {"artifact_name": art_entry}
            elif isinstance(art_entry, tuple):
                args = {"artifact_name": art_entry[0], "version": art_entry[1]}
            else:
                raise ValueError(
                    "An artifact should be passed in as a string or (string, integer) tuple."
                )

            # Retrieve artifact
            try:
                version = args.get("version", None)
                if version is None:
                    art = get(artifact_name=args["artifact_name"])
                else:
                    art = get(
                        artifact_name=args["artifact_name"],
                        version=int(version),
                    )
                if args["artifact_name"] in self.art_name_to_node_id.keys():
                    logger.error("%s is duplicated", args["artifact_name"])
                    raise KeyError("%s is duplicated", args["artifact_name"])
                self.art_name_to_node_id[args["artifact_name"]] = art._node_id
                self.node_id_to_session_id[art._node_id] = art._session_id
            except Exception as e:
                logger.error("Cannot retrive artifact %s", art_entry)
                raise Exception(e)

            # Put artifact in the right session group
            artifacts_by_session[art._session_id] = artifacts_by_session.get(
                art._session_id, []
            ) + [art]

        # For each session, construct SessionArtifacts object
        for session_id, session_artifacts in artifacts_by_session.items():
            self.session_artifacts[session_id] = SessionArtifacts(
                session_artifacts, input_parameters=input_parameters
            )

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
        # Construct a combined graph across multiple sessions
        combined_graph = nx.DiGraph()
        for session_artifacts in self.session_artifacts.values():
            session_graph = session_artifacts.graph.nx_graph
            combined_graph.add_nodes_from(session_graph.nodes)
            combined_graph.add_edges_from(session_graph.edges)

        # Check if user-specified dependency includes artifacts not in the current collection
        dependency_edges = list(
            chain.from_iterable(
                ((artname, to_artname) for artname in from_artname)
                for to_artname, from_artname in dependencies.items()
            )
        )
        dependency_nodes = set(chain(*dependency_edges))
        missing_artifacts = [
            artname
            for artname in dependency_nodes
            if self.art_name_to_node_id.get(artname, None) is None
        ]
        if len(missing_artifacts) > 0:
            raise KeyError(
                f"Dependency graph includes artifact(s) not in this artifact collection: {missing_artifacts}"
            )

        # Augment the graph with user-specified edges
        dependency_edges_by_id = [
            (
                self.art_name_to_node_id.get(edge_tuple[0]),
                self.art_name_to_node_id.get(edge_tuple[1]),
            )
            for edge_tuple in dependency_edges
        ]
        combined_graph.add_edges_from(dependency_edges_by_id)

        # Check if the graph is acyclic
        if nx.is_directed_acyclic_graph(combined_graph) is False:
            raise Exception(
                "LineaPy detected conflict with the provided dependencies. "
                "Please check if the provided dependencies include circular relationships."
            )

        # Identify topological ordering between sessions
        session_id_nodes = list(self.session_artifacts.keys())
        session_id_edges = []
        for node_id, to_node_id in dependency_edges_by_id:
            assert node_id is not None
            assert to_node_id is not None
            from_session_id = self.node_id_to_session_id.get(node_id, None)
            to_session_id = self.node_id_to_session_id.get(to_node_id, None)
            if (
                from_session_id is not None
                and to_session_id is not None
                and from_session_id != to_session_id
            ):
                session_id_edges.append((from_session_id, to_session_id))
        inter_session_graph = nx.DiGraph()
        inter_session_graph.add_nodes_from(session_id_nodes)
        inter_session_graph.add_edges_from(session_id_edges)
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
        session_art1_art2_...
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
