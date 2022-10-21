import logging
from typing import Any, Dict, List

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.task import AirflowDagFlavor, TaskDefinition, TaskGraph
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class AirflowPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "AIRFLOW" framework.
    """

    @property
    def docker_template_name(self) -> str:
        return "airflow_dockerfile.jinja"

    def _write_dag(self) -> None:
        dag_flavor = self.dag_config.get(
            "dag_flavor", "PythonOperatorPerArtifact"
        )

        # Check if the given DAG flavor is a supported/valid one
        if dag_flavor not in AirflowDagFlavor.__members__:
            raise ValueError(
                f'"{dag_flavor}" is an invalid airflow dag flavor.'
            )

        # Construct DAG text for the given flavor

        full_code = self._write_operators(dag_flavor)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(prettify(full_code))
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: str,
    ) -> str:

        DAG_TEMPLATE = load_plugin_template("airflow_dag_PythonOperator.jinja")
        if (
            AirflowDagFlavor[dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerSession
        ):
            task_defs = self.get_session_task_definition()
        elif (
            AirflowDagFlavor[dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerArtifact
        ):
            task_defs = self.get_artifact_task_definitions()

        task_params = self.get_task_params_args(task_defs)
        task_functions = list(task_defs.keys())
        rendered_task_definitions = self.get_rendered_task_definitions(
            task_defs
        )
        dependencies = {
            task_functions[i + 1]: {task_functions[i]}
            for i in range(len(task_functions) - 1)
        }
        task_graph = TaskGraph(
            nodes=task_functions,
            mapping={f: f for f in task_functions},
            edges=dependencies,
        )
        tasks = [
            {"name": ft, "op_kwargs": task_params.get(ft, None)}
            for ft in task_functions
        ]
        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.pipeline_name,
            MODULE_NAME=self.pipeline_name + "_module",
            OWNER=self.dag_config.get("owner", "airflow"),
            RETRIES=self.dag_config.get("retries", 2),
            START_DATE=self.dag_config.get("start_date", "days_ago(1)"),
            SCHEDULE_INTERVAL=self.dag_config.get(
                "schedule_interval", "*/15 * * * *"
            ),
            dag_params=self.get_airflow_pipeline_args(),
            MAX_ACTIVE_RUNS=self.dag_config.get("max_active_runs", 1),
            CATCHUP=self.dag_config.get("catchup", "False"),
            task_definitions=rendered_task_definitions,
            tasks=tasks,
            task_dependencies=task_graph.get_airflow_dependencies(
                setup_task="setup", teardown_task="teardown"
            ),
        )

        return full_code

    def get_airflow_pipeline_args(self) -> str:
        """
        get_pipeline_args returns the DAG parameters for an Airflow Pipeline.
        This is formatted in an Airflow friendly format.

        Example:

        "params":{
            a: "value",
            b: 0,
        }
        """
        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_pipeline_args().items():
            input_parameters_dict[parameter_name] = input_spec.value
        return '"params":' + str(input_parameters_dict)

    def get_task_params_args(
        self, pipeline_task: Dict[str, TaskDefinition]
    ) -> Dict[str, str]:
        function_input_parameters = dict()
        for task_name, taskdef in pipeline_task.items():
            if len(taskdef.user_input_variables) > 0:
                function_input_parameters[task_name] = "op_kwargs=" + str(
                    {
                        var: "{{ params." + var + " }}"
                        for var in taskdef.user_input_variables
                    }
                )
        return function_input_parameters

    def get_rendered_task_definitions(
        self,
        pipeline_task: Dict[str, TaskDefinition],
        indentation=4,
    ) -> List[str]:

        TASK_FUNCTION_TEMPLATE = load_plugin_template("task_function.jinja")
        task_defs: List[str] = []
        for task_name, taskdef in pipeline_task.items():
            function_definition = TASK_FUNCTION_TEMPLATE.render(
                function_name=task_name,
                user_input_variables=", ".join(taskdef.user_input_variables),
                typing_blocks=taskdef.typing_blocks,
                loading_blocks=taskdef.loading_blocks,
                call_block=taskdef.call_block,
                dumping_blocks=taskdef.dumping_blocks,
                indentation_block=" " * indentation,
            )
            task_defs.append(function_definition)

        return task_defs
