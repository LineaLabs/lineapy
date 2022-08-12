import logging
from pathlib import Path
from typing import Dict, List, Optional

from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.graph_reader.node_collection import NodeCollection
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.plugins.task import (
    AirflowDagConfig,
    AirflowDagFlavor,
    TaskGraph,
    TaskGraphEdge,
)
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import get_system_python_version, prettify

logger = logging.getLogger(__name__)
configure_logging()


def generate_pipeline_files(
    artifact_collection: ArtifactCollection,
    framework: str = "SCRIPT",
    dependencies: TaskGraphEdge = {},
    keep_lineapy_save: bool = False,
    pipeline_name: str = "pipeline",
    output_dir: str = ".",
    dag_config: Optional[AirflowDagConfig] = {},
):
    """
    Use modularized artifact code to generate standard pipeline files,
    including Python modules, DAG script, and infra files (e.g., Dockerfile).
    Actual code generation and writing is delegated to the "writer" class
    for each framework type (e.g., "SCRIPT").
    """
    output_path = Path(output_dir, pipeline_name)
    output_path.mkdir(exist_ok=True, parents=True)

    # Sort sessions topologically (applicable if artifacts come from multiple sessions)
    session_artifacts_sorted = artifact_collection._sort_session_artifacts(
        dependencies=dependencies
    )

    # Write out module file
    module_text = artifact_collection._compose_module(
        session_artifacts_sorted=session_artifacts_sorted,
        indentation=4,
    )
    module_file = output_path / f"{pipeline_name}_module.py"
    module_file.write_text(prettify(module_text))
    logger.info("Generated module file")

    # Write out requirements file
    # TODO: Filter relevant imports only (i.e., those "touched" by artifacts in pipeline)
    db = session_artifacts_sorted[0].db
    libraries = dict()
    for session_artifacts in session_artifacts_sorted:
        session_libs = db.get_libraries_for_session(
            session_artifacts.session_id
        )
        for lib in session_libs:
            libraries[lib.package_name] = lib.version
    lib_names_text = "\n".join(
        [f"{lib}=={ver}" for lib, ver in libraries.items()]
    )
    requirements_file = output_path / f"{pipeline_name}_requirements.txt"
    requirements_file.write_text(lib_names_text)
    logger.info("Generated requirements file")

    pipeline_writer: BasePipelineWriter

    # Delegate to framework-specific writer
    if framework in PipelineType.__members__:
        if PipelineType[framework] == PipelineType.AIRFLOW:
            pipeline_writer = AirflowPipelineWriter(
                session_artifacts_sorted=session_artifacts_sorted,
                keep_lineapy_save=keep_lineapy_save,
                pipeline_name=pipeline_name,
                output_dir=output_dir,
                dag_config=dag_config,
            )
        else:
            pipeline_writer = BasePipelineWriter(
                session_artifacts_sorted=session_artifacts_sorted,
                keep_lineapy_save=keep_lineapy_save,
                pipeline_name=pipeline_name,
                output_dir=output_dir,
            )
    else:
        raise ValueError(f'"{framework}" is an invalid value for framework.')

    return pipeline_writer.write_pipeline_files()


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

    def _write_docker(
        self, template_name: str, template_params: Dict[str, str]
    ) -> None:
        # Generate Dockerfile text
        DOCKERFILE_TEMPLATE = load_plugin_template(template_name)
        dockerfile_text = DOCKERFILE_TEMPLATE.render(**template_params)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_Dockerfile"
        file.write_text(dockerfile_text)

        logger.info("Generated Docker file")

    def write_pipeline_files(self) -> None:
        self._write_docker(
            template_name="script_dockerfile.jinja",
            template_params={
                "pipeline_name": self.pipeline_name,
                "python_version": get_system_python_version(),
            },
        )


class AirflowPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "AIRFLOW" framework.
    """

    def __init__(
        self, dag_config: Optional[AirflowDagConfig] = {}, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.dag_config = dag_config or {}

    def _write_dag(self) -> None:
        dag_flavor = self.dag_config.get(
            "dag_flavor", AirflowDagFlavor.PythonOperatorPerSession
        )

        if dag_flavor == AirflowDagFlavor.PythonOperatorPerSession:
            DAG_TEMPLATE = load_plugin_template(
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
            full_code = DAG_TEMPLATE.render(
                DAG_NAME=self.pipeline_name,
                MODULE_NAME=self.pipeline_name + "_module",
                OWNER=self.dag_config.get("owner", "airflow"),
                RETRIES=self.dag_config.get("retries", 2),
                START_DATE=self.dag_config.get("start_date", "days_ago(1)"),
                SCHEDULE_INTERVAL=self.dag_config.get(
                    "schedule_interval", "*/15 * * * *"
                ),
                MAX_ACTIVE_RUNS=self.dag_config.get("max_active_runs", 1),
                CATCHUP=self.dag_config.get("catchup", "False"),
                tasks=session_functions,
                task_dependencies=task_graph.get_airflow_dependency(),
            )
            full_code = prettify(full_code)

            # Write out file
            file = self.output_dir / f"{self.pipeline_name}_dag.py"
            file.write_text(prettify(full_code))
            logger.info("Generated DAG file %s", file)
        elif dag_flavor == AirflowDagFlavor.PythonOperatorPerArtifact:
            DAG_TEMPLATE = load_plugin_template(
                "airflow_dag_PythonOperatorPerArtifact.jinja"
            )
            task_functions = []
            task_definitions = []
            for session_artifacts in self.session_artifacts_sorted:
                task_functions += [
                    nc.safename
                    for nc in session_artifacts.artifact_nodecollections
                ]
                task_definitions += [
                    get_task(nc, self.pipeline_name)
                    for nc in session_artifacts.artifact_nodecollections
                ]
            for callblock in task_definitions:
                print(callblock)
            dependencies = {
                task_functions[i + 1]: {task_functions[i]}
                for i in range(len(task_functions) - 1)
            }
            task_graph = TaskGraph(
                nodes=[f[0] for f in task_functions],
                mapping={f[0]: f[0] for f in task_functions},
                edges=dependencies,
            )
            full_code = DAG_TEMPLATE.render(
                DAG_NAME=self.pipeline_name,
                MODULE_NAME=self.pipeline_name + "_module",
                OWNER=self.dag_config.get("owner", "airflow"),
                RETRIES=self.dag_config.get("retries", 2),
                START_DATE=self.dag_config.get("start_date", "days_ago(1)"),
                SCHEDULE_INTERVAL=self.dag_config.get(
                    "schedule_interval", "*/15 * * * *"
                ),
                MAX_ACTIVE_RUNS=self.dag_config.get("max_active_runs", 1),
                CATCHUP=self.dag_config.get("catchup", "False"),
                task_definitions=task_definitions,
                tasks=task_functions,
                task_dependencies=task_graph.get_airflow_dependency(),
            )
            full_code = prettify(full_code)

            # Write out file
            file = self.output_dir / f"{self.pipeline_name}_dag.py"
            file.write_text(prettify(full_code))
            logger.info("Generated DAG file %s", file)
        else:
            raise ValueError(
                f'"{dag_flavor}" is an invalid airflow dag flavor.'
            )

    def write_pipeline_files(self) -> None:
        self._write_dag()
        self._write_docker(
            template_name="dockerfile.jinja",
            template_params={
                "pipeline_name": self.pipeline_name,
                "python_version": get_system_python_version(),
            },
        )


def get_task(nc: NodeCollection, pipeline_name: str, indentation=4) -> str:
    input_var_loading_block = [
        f"{var} = pickle.load(open('/tmp/{pipeline_name}/variable_{var}.pickle','rb'))"
        for var in nc.input_variables
    ]
    function_call_block = f"{nc.get_function_call_block(indentation=0)}"
    return_var_saving_block = [
        f"pickle.dump({var},open('/tmp/{pipeline_name}/variable_{var}.pickle','wb'))"
        for var in nc.input_variables
    ]

    TASK_FUNCITON_TEMPLATE = load_plugin_template("task_function.jinja")
    return TASK_FUNCITON_TEMPLATE.render(
        artifact_name=nc.safename,
        loading_blocks=input_var_loading_block,
        call_block=function_call_block,
        dumping_block=return_var_saving_block,
        indentation_block=" " * indentation,
    )
