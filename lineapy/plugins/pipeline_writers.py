import logging
from pathlib import Path
from typing import Dict, List, Optional

from lineapy.api.api_utils import de_lineate_code
from lineapy.graph_reader.node_collection import NodeCollectionType
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.plugins.task import AirflowDagConfig, AirflowDagFlavor, TaskGraph
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class BasePipelineWriter:
    """
    Base class for pipeline file writer. Corresponds to "SCRIPT" framework.
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

        # We assume there is at least one SessionArtifacts object
        self.db = self.session_artifacts_sorted[0].db

    def _write_dag(self) -> None:
        # Initiate store for DAG script components
        main_module_dict: Dict[str, List[str]] = {
            "import_lines": [],
            "calculation_lines": [],
            "return_varnames": [],
        }

        # Extract script components by session
        for session_artifacts in self.session_artifacts_sorted:
            # Generate import statements
            func_names = [
                f"get_{coll.safename}"
                for coll in session_artifacts.artifact_nodecollections
            ]
            main_module_dict["import_lines"].append(
                f"from {self.pipeline_name}_module import {', '.join(func_names)}"
            )

            # Generate calculation lines
            calc_lines = [
                coll.get_function_call_block(
                    indentation=4, keep_lineapy_save=self.keep_lineapy_save
                )
                for coll in session_artifacts.artifact_nodecollections
            ]
            main_module_dict["calculation_lines"].extend(calc_lines)

            # Generate return variables
            ret_varnames = [
                coll.return_variables[0]
                for coll in session_artifacts.artifact_nodecollections
                if coll.collection_type == NodeCollectionType.ARTIFACT
            ]
            main_module_dict["return_varnames"].extend(ret_varnames)

        # Combine components by "type"
        imports = "\n".join(main_module_dict["import_lines"])
        calculations = "\n".join(main_module_dict["calculation_lines"])
        returns = ", ".join(main_module_dict["return_varnames"])

        # Put all together to DAG script text
        # TODO: Replace with jinja template
        script_dag_text = f"""\
{imports}

def pipeline():
{calculations}
    return {returns}

if __name__ == "__main__":
    pipeline()
"""

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_script_dag.py"
        file.write_text(prettify(de_lineate_code(script_dag_text, self.db)))

        logger.info("Generated DAG file")

    def _write_docker(self):
        # Generate Dockerfile text
        DOCKERFILE_TEMPLATE = load_plugin_template("script_dockerfile.jinja")
        dockerfile_text = DOCKERFILE_TEMPLATE.render(
            pipeline_name=self.pipeline_name
        )

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_Dockerfile"
        file.write_text(dockerfile_text)

        logger.info("Generated Docker file")

    def write_pipeline_files(self) -> None:
        self._write_dag()
        self._write_docker()


class AirflowPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "AIRFLOW" framework.
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

        # We assume there is at least one SessionArtifacts object
        self.db = self.session_artifacts_sorted[0].db

    def _write_dag(
        self,
        airflow_dag_config: Optional[AirflowDagConfig] = {},
        airflow_dag_flavor: str = "PythonOperatorPerSession",
    ) -> None:
        airflow_dag_config = airflow_dag_config or {}
        if (
            AirflowDagFlavor[airflow_dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerSession
        ):
            AIRFLOW_DAG_TEMPLATE = load_plugin_template(
                "airflow_dag_PythonOperatorPerSession.jinja"
            )
            session_functions = [
                f"run_session_including_{session_artifacts._get_first_artifact_name()}"
                for session_artifacts in self.session_artifacts_sorted
            ]
            dependencies = {
                session_functions[i + 1]: {session_functions[i]}
                for i in range(len(session_functions) - 1)
            }
            task_graph = TaskGraph(
                nodes=session_functions,
                mapping={f: f for f in session_functions},
                edges=dependencies,
            )
            full_code = AIRFLOW_DAG_TEMPLATE.render(
                DAG_NAME=self.pipeline_name,
                MODULE_NAME=self.pipeline_name + "_module",
                OWNER=airflow_dag_config.get("owner", "airflow"),
                RETRIES=airflow_dag_config.get("retries", 2),
                START_DATE=airflow_dag_config.get("start_date", "days_ago(1)"),
                SCHEDULE_INTERVAL=airflow_dag_config.get(
                    "schedule_interval", "*/15 * * * *"
                ),
                MAX_ACTIVE_RUNS=airflow_dag_config.get("max_active_runs", 1),
                CATCHUP=airflow_dag_config.get("catchup", "False"),
                tasks=session_functions,
                task_dependencies=task_graph.get_airflow_dependency(),
            )
            full_code = prettify(full_code)

            # Write out file
            file = self.output_dir / f"{self.pipeline_name}_dag.py"
            file.write_text(prettify(full_code))
            logger.info("Generated DAG file %s", file)
        else:
            raise ValueError(
                f'"{airflow_dag_flavor}" is an invalid airflow dag flavor.'
            )

    def _write_docker(self):
        # Generate Dockerfile text
        DOCKERFILE_TEMPLATE = load_plugin_template("dockerfile.jinja")
        dockerfile_text = DOCKERFILE_TEMPLATE.render(
            pipeline_name=self.pipeline_name
        )

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_Dockerfile"
        file.write_text(dockerfile_text)
        logger.info("Generated Docker file %s", file)

    def write_pipeline_files(self) -> None:
        self._write_dag()
        self._write_docker()
