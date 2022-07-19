import logging
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Dict, List, Tuple, Union

import networkx as nx

from lineapy.api.api import get
from lineapy.api.api_classes import LineaArtifact
from lineapy.data.types import LineaID, PipelineType
from lineapy.graph_reader.graph_refactorer import (
    GraphSegmentType,
    SessionArtifacts,
)
from lineapy.plugins.task import TaskGraphEdge
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

    def __init__(self, artifacts=List[Union[str, Tuple[str, int]]]) -> None:
        self.session_artifacts: Dict[LineaID, SessionArtifacts] = {}
        self.art_name_to_node_id: Dict[str, LineaID] = {}
        self.node_id_to_session_id: Dict[LineaID, LineaID] = {}

        artifacts_by_session: Dict[LineaID, List[LineaArtifact]] = {}

        # Retrieve artifact objects and group them by session ID
        for art_entry in artifacts:
            # Construct args for artifact retrieval
            args = {}
            if isinstance(art_entry, str):
                args["artifact_name"] = art_entry
            elif isinstance(art_entry, tuple):
                args["artifact_name"] = art_entry[0]
                args["version"] = art_entry[1]
            else:
                raise ValueError(
                    "An artifact should be passed in as a string or (string, integer) tuple."
                )

            # Retrieve artifact
            try:
                art = get(**args)
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
                session_artifacts
            )

    def _sort_session_artifacts(
        self, dependencies: TaskGraphEdge = {}
    ) -> List[SessionArtifacts]:
        """
        Use the user-provided artifact dependencies to
        topologically sort a list of SessionArtifacts objects.
        Raise an exception if the graph contains a cycle.
        """
        # Construct a combined graph across multiple sessions
        combined_graph = nx.DiGraph()
        for session_artifacts in self.session_artifacts.values():
            session_graph = session_artifacts.graph.nx_graph
            combined_graph.add_nodes_from(session_graph.nodes)
            combined_graph.add_edges_from(session_graph.edges)

        # Augment the graph with user-specified edges
        dependency_edges = list(
            chain.from_iterable(
                (
                    (
                        self.art_name_to_node_id.get(artname, None),
                        self.art_name_to_node_id.get(to_artname, None),
                    )
                    for artname in from_artname
                )
                for to_artname, from_artname in dependencies.items()
            )
        )
        if None in list(chain.from_iterable(dependency_edges)):
            raise KeyError(
                "Dependency graph includes artifacts not in this artifact collection."
            )
        combined_graph.add_edges_from(dependency_edges)

        # Check if the graph is acyclic
        if nx.is_directed_acyclic_graph(combined_graph) is False:
            raise Exception("Provided dependencies result in a cyclic graph.")

        # Identify topological ordering between sessions
        session_id_nodes = list(self.session_artifacts.keys())
        session_id_edges = [
            (
                self.node_id_to_session_id.get(node_id, None),
                self.node_id_to_session_id.get(to_node_id, None),
            )
            for node_id, to_node_id in dependency_edges
            if self.node_id_to_session_id.get(node_id, None)
            != self.node_id_to_session_id.get(to_node_id, None)
        ]
        inter_session_graph = nx.DiGraph()
        inter_session_graph.add_nodes_from(session_id_nodes)
        inter_session_graph.add_edges_from(session_id_edges)
        session_id_sorted = nx.topological_sort(inter_session_graph)

        return [
            self.session_artifacts[session_id]
            for session_id in session_id_sorted
        ]

    def generate_pipeline_files(
        self,
        framework: str = "SCRIPT",
        dependencies: TaskGraphEdge = {},
        keep_lineapy_save: bool = False,
        pipeline_name: str = "pipeline",
        output_dir: str = ".",
    ):
        """
        Use modularized artifact code to generate standard pipeline files,
        including Python modules, DAG script, and infra files (e.g., Dockerfile).

        Actual code generation and writing is delegated to the "writer" class
        for each framework type (e.g., "SCRIPT").
        """

        # Sort SessionArtifacts objects topologically
        session_artifacts_sorted = self._sort_session_artifacts(
            dependencies=dependencies
        )

        if framework in PipelineType.__members__:
            if PipelineType[framework] == PipelineType.AIRFLOW:
                raise NotImplementedError("Airflow writer to be implemented!")
            else:
                pipeline_writer = ScriptPipelineWriter(
                    session_artifacts_sorted=session_artifacts_sorted,
                    keep_lineapy_save=keep_lineapy_save,
                    pipeline_name=pipeline_name,
                    output_dir=output_dir,
                )
        else:
            raise ValueError(
                f'"{framework}" is an invalid value for framework.'
            )

        return pipeline_writer.write_pipeline_files()


class BasePipelineWriter:
    """
    Base class for pipeline file writer.
    """

    def __init__(
        self,
        session_artifacts_sorted: List[SessionArtifacts],
        keep_lineapy_save: bool,
        pipeline_name: str,
        output_dir: str,
    ) -> None:
        self.session_artifacts_sorted = session_artifacts_sorted
        self.keep_lineapy_save = keep_lineapy_save
        self.pipeline_name = pipeline_name
        self.output_dir = Path(output_dir, pipeline_name)

        # Create output directory folder(s) if nonexistent
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def _write_modules(self) -> None:
        files_dict = {}
        for session_artifacts in self.session_artifacts_sorted:
            # Generate session module code
            for seg in session_artifacts.graph_segments:
                if seg.segment_type == GraphSegmentType.ARTIFACT:
                    first_art_name = seg.artifact_safename
                    break
            module_name = f"session_including_artifact_{first_art_name}"
            files_dict[
                module_name
            ] = session_artifacts.get_session_module_definition(
                indentation=4, keep_lineapy_save=self.keep_lineapy_save
            )

        # Write out file(s)
        for name, content in files_dict.items():
            (self.output_dir / f"{name}.py").write_text(content)

        logger.info("Generated session module files")

    def _write_requirements(self) -> None:
        # TODO: Filter relevant imports only (i.e., those "touched" by artifacts in pipeline)
        lib_names_text = ""
        for session_artifacts in self.session_artifacts_sorted:
            session_libs = session_artifacts.db.get_libraries_for_session(
                session_artifacts.session_id
            )
            for lib in session_libs:
                lib_names_text += f"{lib.package_name}=={lib.version}\n"

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_requirements.txt"
        file.write_text(lib_names_text)

        logger.info("Generated requirements file")

    def _write_dag(self):
        raise NotImplementedError

    def _write_docker(self):
        raise NotImplementedError

    def write_pipeline_files(self):
        raise NotImplementedError


class ScriptPipelineWriter(BasePipelineWriter):
    """
    Pipeline file writer for "SCRIPT" framework.
    """

    def _write_dag(self) -> None:
        # Initiate main module (which imports and combines session modules)
        main_module_dict = {
            "import_lines": [],
            "calculation_lines": [],
            "return_varnames": [],
        }

        for session_artifacts in self.session_artifacts_sorted:
            # Generate session module code
            for seg in session_artifacts.graph_segments:
                if seg.segment_type == GraphSegmentType.ARTIFACT:
                    first_art_name = seg.artifact_safename
                    break
            module_name = f"session_including_artifact_{first_art_name}"

            # Generate import statements for main module
            func_names = [
                f"get_{seg.artifact_safename}"
                for seg in session_artifacts.graph_segments
            ]
            main_module_dict["import_lines"].append(
                f"from {module_name} import {', '.join(func_names)}"
            )

            # Generate calculation lines for main module
            calc_lines = [
                seg.get_function_call_block(
                    indentation=4, keep_lineapy_save=self.keep_lineapy_save
                )
                for seg in session_artifacts.graph_segments
            ]
            main_module_dict["calculation_lines"].extend(calc_lines)

            # Generate return variables for main module
            ret_varnames = [
                seg.return_variables[0]
                for seg in session_artifacts.graph_segments
                if seg.segment_type == GraphSegmentType.ARTIFACT
            ]
            main_module_dict["return_varnames"].extend(ret_varnames)

        # Generate main module code
        imports = "\n".join(main_module_dict["import_lines"])
        calculations = "\n".join(main_module_dict["calculation_lines"])
        returns = ", ".join(main_module_dict["return_varnames"])
        script_dag_text = f"""
{imports}

def pipeline():
{calculations}
    return {returns}

if __name__=='__main__':
    pipeline()
"""

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_script_dag.py"
        file.write_text(script_dag_text)

        logger.info("Generated dag file")

    def write_pipeline_files(self) -> None:
        self._write_modules()
        self._write_requirements()
        self._write_dag()


class AirflowPipelineWriter(BasePipelineWriter):
    pass
