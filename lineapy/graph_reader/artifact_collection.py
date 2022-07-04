import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from lineapy.api.api import get
from lineapy.api.api_classes import LineaArtifact
from lineapy.data.types import LineaID
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
    A collection of artifacts, which can perform various code transformations
    such as graph refactor for pipeline building.
    """

    artifacts_by_session: Dict[LineaID, List[LineaArtifact]]
    session_artifacts: Dict[LineaID, SessionArtifacts]
    artifact_node_id: Dict[str, LineaID]

    def __init__(self, artifacts=List[Union[str, Tuple[str, int]]]) -> None:
        self.artifacts_by_session = {}
        self.session_artifacts = {}
        self.artifact_node_id = {}

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
                self.artifact_node_id[args["artifact_name"]] = art._node_id
            except Exception as e:
                logger.error("Cannot retrive artifact %s", art_entry)
                raise Exception(e)

            # Put artifact in the right session group
            self.artifacts_by_session[
                art._session_id
            ] = self.artifacts_by_session.get(art._session_id, []) + [art]

        # For each session, construct SessionArtifacts object
        for session_id, session_artifacts in self.artifacts_by_session.items():
            self.session_artifacts[session_id] = SessionArtifacts(
                session_artifacts
            )

    def generate_python_modules(
        self, dependencies: TaskGraphEdge = {}, keep_lineapy_save: bool = False
    ) -> dict:
        # TODO: Take in task dependency as user input and check it is acyclic
        dependencies

        # Initiate main module (which imports and combines session modules)
        main_module_dict = {
            "import_lines": [],
            "calculation_lines": [],
            "return_varnames": [],
        }

        python_modules = {}
        for session_artifacts in self.session_artifacts.values():
            # Generate session module code
            first_art_name = session_artifacts.graph_segments[0].artifact_name
            module_name = f"session_including_artifact_{first_art_name}"
            python_modules[
                module_name
            ] = session_artifacts.get_session_module_definition(
                indentation=4, keep_lineapy_save=keep_lineapy_save
            )

            # Generate import statements for main module
            func_names = [
                f"get_{seg.artifact_name}"
                for seg in session_artifacts.graph_segments
            ]
            main_module_dict["import_lines"].append(
                f"from {module_name} import {', '.join(func_names)}"
            )

            # Generate calculation lines for main module
            calc_lines = [
                seg.get_function_call_block(
                    indentation=4, keep_lineapy_save=keep_lineapy_save
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
        python_modules[
            "main"
        ] = f"""
{imports}

def pipeline():
{calculations}
    return {returns}

if __name__=='__main__':
    pipeline()
"""

        return python_modules
