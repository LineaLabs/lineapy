import logging
from pathlib import Path
from typing import Dict, List, Optional

from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
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


class RayWorkflowPipelineWriter(BasePipelineWriter):
    def _write_dag(self):
        indentation = 4
        graphs = []
        artifacts = []
        function_definitions = []
        name_to_output = {}
        name_to_input = {}
        for session_artifacts in self.session_artifacts_sorted:
            function_definitions.append("\n\n".join(
                [
                    nodecollection.get_function_definition(indentation=indentation)
                    for nodecollection in session_artifacts.artifact_nodecollections
                ]
            ))
            artifacts += session_artifacts.artifact_list
            graphs.append(session_artifacts.nodecollection_dependencies)
            name_to_output.update(
                {nc.name: nc.return_variables for nc in session_artifacts.artifact_nodecollections}
            )
            name_to_input.update(
                {nc.name: nc.input_variables for nc in session_artifacts.artifact_nodecollections}
            )

        with open(self.output_dir / f"{self.pipeline_name}_ray_dag.py", mode="w") as w:
            w.write("""
import ray
import ray.workflow as workflow
import os
assert os.environ.get("RAY_ADDRESS") is not None
ray.init(address=os.environ["RAY_ADDRESS"])
workflow.init()\n""")
            w.write("\n".join(function_definitions))
            w.write("\n")
            # assume only one graph for now
            assert len(graphs) == 1
            task_order = graphs[0].get_taskorder()
            for task in task_order:
                ray_func = f"""
@ray.remote
def _ray_{task}(*args):
    inputs = {{k: v for d in args for k, v in d.items()}}
    rets = get_{task}(**inputs)
    outputs = {name_to_output[task]}
    if not isinstance(rets, (list, tuple)): rets = [rets]
    return dict(zip(outputs, rets))
"""
                w.write(ray_func)
                pred = list(graphs[0].graph.predecessors(task))
                pred_inputs = ', '.join([f"_ray_{p}_node" for p in pred])
                w.write(f"_ray_{task}_node = _ray_{task}.bind({pred_inputs})\n")

            print(artifacts)
            results = ','.join([f"_ray_{a.name}_node" for a in artifacts])
            # names = ','.join([f"'{a.name}'" for a in artifacts])
            w.write(f"""
@ray.remote(**workflow.options(checkpoint=False))
def gather(*args):
    return {{k: v for d in args for k, v in d.items()}}

_dag = gather.bind({results})
workflow_id = os.environ.get("WORKFLOD_ID")
# if not set, random id will be generated.
# we might want:
# 1. pass workflow id with cli.
# 2. choose to resume or just start a new one.
print(ray.workflow.run(_dag, workflow_id))
""")
            # w.write(str(name_to_output) + "\n")
            # w.write(str(name_to_input) + "\n")



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
