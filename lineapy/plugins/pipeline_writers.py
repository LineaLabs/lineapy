import logging
from pathlib import Path
from typing import Dict, Optional

from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.graph_reader.node_collection import NodeCollection
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


class BasePipelineWriter:
    """
    Pipeline writer uses modularized artifact code to generate
    and write out standard pipeline files, including Python modules,
    DAG script, and infra files (e.g., Dockerfile).

    Base class for pipeline file writer corresponds to "SCRIPT" framework.
    """

    def __init__(
        self,
        artifact_collection: ArtifactCollection,
        dependencies: TaskGraphEdge = {},
        keep_lineapy_save: bool = False,
        pipeline_name: str = "pipeline",
        output_dir: str = ".",
        dag_config: Optional[AirflowDagConfig] = {},
    ) -> None:
        self.artifact_collection = artifact_collection
        self.keep_lineapy_save = keep_lineapy_save
        self.pipeline_name = pipeline_name
        self.output_dir = Path(output_dir, pipeline_name)
        self.dag_config = dag_config or {}

        # Sort sessions topologically (applicable if artifacts come from multiple sessions)
        self.session_artifacts_sorted = (
            artifact_collection._sort_session_artifacts(
                dependencies=dependencies
            )
        )

        # Create output directory folder(s) if nonexistent
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # We assume there is at least one SessionArtifacts object
        self.db = self.session_artifacts_sorted[0].db

    @property
    def docker_template_name(self) -> str:
        return "script_dockerfile.jinja"

    @property
    def docker_template_params(self) -> Dict[str, str]:
        return {
            "pipeline_name": self.pipeline_name,
            "python_version": get_system_python_version(),
        }

    def _write_module(self) -> None:
        """
        Write out module file containing refactored code.
        """
        module_text = self.artifact_collection._compose_module(
            session_artifacts_sorted=self.session_artifacts_sorted,
            indentation=4,
        )
        file = self.output_dir / f"{self.pipeline_name}_module.py"
        file.write_text(prettify(module_text))
        logger.info(f"Generated module file: {file}")

    def _write_requirements(self) -> None:
        """
        Write out requirements file.
        """
        # TODO: Filter relevant imports only (i.e., those "touched" by artifacts in pipeline)
        libraries = dict()
        for session_artifacts in self.session_artifacts_sorted:
            session_libs = self.db.get_libraries_for_session(
                session_artifacts.session_id
            )
            for lib in session_libs:
                libraries[lib.package_name] = lib.version
        lib_names_text = "\n".join(
            [
                lib if lib == "lineapy" else f"{lib}=={ver}"
                for lib, ver in libraries.items()
            ]
        )
        file = self.output_dir / f"{self.pipeline_name}_requirements.txt"
        file.write_text(lib_names_text)
        logger.info(f"Generated requirements file: {file}")

    def _write_dag(self) -> None:
        """
        Write out framework-specific DAG file
        """
        pass  # SCRIPT framework does not need DAG file

    def _write_docker(self) -> None:
        """
        Write out Docker file.
        """
        DOCKERFILE_TEMPLATE = load_plugin_template(self.docker_template_name)
        dockerfile_text = DOCKERFILE_TEMPLATE.render(
            **self.docker_template_params
        )
        file = self.output_dir / f"{self.pipeline_name}_Dockerfile"
        file.write_text(dockerfile_text)
        logger.info(f"Generated Docker file: {file}")

    def write_pipeline_files(self) -> None:
        """
        Write out pipeline files.
        """
        self._write_module()
        self._write_requirements()
        self._write_dag()
        self._write_docker()


class AirflowPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "AIRFLOW" framework.
    """

    @property
    def docker_template_name(self) -> str:
        return "airflow_dockerfile.jinja"

    def _write_dag(self) -> None:
        dag_flavor = self.dag_config.get(
            "dag_flavor", "PythonOperatorPerSession"
        )

        # Check if the given DAG flavor is a supported/valid one
        if dag_flavor not in AirflowDagFlavor.__members__:
            raise ValueError(
                f'"{dag_flavor}" is an invalid airflow dag flavor.'
            )

        # Construct DAG text for the given flavor
        if (
            AirflowDagFlavor[dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerSession
        ):
            full_code = self._write_operator_per_session()
        elif (
            AirflowDagFlavor[dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerArtifact
        ):
            full_code = self._write_operator_per_artifact()

        # Write out file
        full_code = prettify(full_code)
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(prettify(full_code))
        logger.info(f"Generated DAG file: {file}")

    def _write_operator_per_session(self) -> str:
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
            task_dependencies=task_graph.get_airflow_dependencies(),
        )

        return full_code

    def _write_operator_per_artifact(self) -> str:
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
                get_task_definition(nc, self.pipeline_name)
                for nc in session_artifacts.artifact_nodecollections
            ]
        dependencies = {
            task_functions[i + 1]: {task_functions[i]}
            for i in range(len(task_functions) - 1)
        }
        task_graph = TaskGraph(
            nodes=task_functions,
            mapping={f: f for f in task_functions},
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
            task_dependencies=task_graph.get_airflow_dependencies(
                setup_task="setup", teardown_task="teardown"
            ),
        )

        return full_code


def get_task_definition(
    nc: NodeCollection, pipeline_name: str, indentation=4
) -> str:
    """
    Add deserialization of input variables and serialization of output
    variables logic of the call_block and wrap them into a new function
    definition.
    """
    input_var_loading_block = [
        f"{var} = pickle.load(open('/tmp/{pipeline_name}/variable_{var}.pickle','rb'))"
        for var in sorted(list(nc.input_variables))
    ]
    function_call_block = nc.get_function_call_block(
        indentation=0, source_module=f"{pipeline_name}_module"
    )
    return_var_saving_block = [
        f"pickle.dump({var},open('/tmp/{pipeline_name}/variable_{var}.pickle','wb'))"
        for var in nc.return_variables
    ]

    TASK_FUNCTION_TEMPLATE = load_plugin_template("task_function.jinja")
    return TASK_FUNCTION_TEMPLATE.render(
        artifact_name=nc.safename,
        loading_blocks=input_var_loading_block,
        call_block=function_call_block,
        dumping_blocks=return_var_saving_block,
        indentation_block=" " * indentation,
    )


class PipelineWriterFactory:
    @classmethod
    def get(
        cls,
        pipeline_type: PipelineType = PipelineType.SCRIPT,
        *args,
        **kwargs,
    ):
        if pipeline_type == PipelineType.AIRFLOW:
            return AirflowPipelineWriter(*args, **kwargs)
        else:
            return BasePipelineWriter(*args, **kwargs)
