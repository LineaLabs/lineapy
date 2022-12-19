import logging
from enum import Enum
from typing import Any, Dict, List

from typing_extensions import TypedDict

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.task import (
    DagTaskBreakdown,
    TaskDefinition,
    TaskSerializer,
    render_task_io_serialize_blocks,
)
from lineapy.plugins.taskgen import (
    get_localpickle_setup_task_definition,
    get_localpickle_teardown_task_definition,
    get_task_graph,
)
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class AirflowDagFlavor(Enum):
    PythonOperatorPerSession = 1
    PythonOperatorPerArtifact = 2
    # To be implemented for different flavor of airflow dags
    # BashOperator = 3
    # DockerOperator = 4
    # KubernetesPodOperator = 5


AirflowDagConfig = TypedDict(
    "AirflowDagConfig",
    {
        "owner": str,
        "retries": int,
        "start_date": str,
        "schedule_interval": str,
        "max_active_runs": int,
        "catchup": str,
        "dag_flavor": str,  # Not native to Airflow config
        "task_serialization": str,  # Not native to Airflow config
    },
    total=False,
)


class AirflowPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "AIRFLOW" framework.
    """

    @property
    def docker_template_name(self) -> str:
        return "airflow_dockerfile.jinja"

    def _write_dag(self) -> None:

        # Check if the given DAG flavor is a supported/valid one
        try:
            dag_flavor = AirflowDagFlavor[
                self.dag_config.get("dag_flavor", "PythonOperatorPerArtifact")
            ]
        except KeyError:
            raise ValueError(
                f'"{dag_flavor}" is an invalid airflow dag flavor.'
            )

        try:
            task_serialization = TaskSerializer[
                self.dag_config.get("task_serialization", "LocalPickle")
            ]
        except KeyError:
            raise ValueError(
                f'"{task_serialization}" is an invalid type of task serialization scheme.'
            )

        # Construct DAG text for the given flavor
        full_code = self._write_operators(dag_flavor, task_serialization)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(prettify(full_code))
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: AirflowDagFlavor,
        task_serialization: TaskSerializer,
    ) -> str:
        """
        This method implements Airflow DAG code generation corresponding
        to the following flavors

        - ``PythonOperatorPerSession`` flavor, where each session gets its
        own Python operator.
        - ``PythonOperatorPerArtifact`` flavor, where each artifact gets its own
        Python operator.

        Example of ``PythonOperatorPerSession`` if the two artifacts in our pipeline
        (e.g., model and prediction) were created in the same session.
        .. code-block:: python
            import pickle
            import g2_z_module
            ...
            def task_run_session_including_g2():
                artifacts = g2_z_module.run_session_including_g2()
                pickle.dump(artifacts["g2"], open("/tmp/g2_z/artifact_g2.pickle", "wb"))
                pickle.dump(artifacts["z"], open("/tmp/g2_z/artifact_z.pickle", "wb"))
            with DAG(...) as dag:
                run_session_including_g2 = PythonOperator(
                    task_id="run_session_including_g2_task",
                    python_callable=task_run_session_including_g2,
                )

        Example of ``PythonOperatorPerArtifact``, if the two artifacts in our pipeline
        (e.g., model and prediction) were created in the same session:
        .. code-block:: python
            import pickle
            import iris_module
            ...
            def task_iris_model():
                mod = iris_module.get_iris_model()
                pickle.dump(mod, open("/tmp/iris/variable_mod.pickle", "wb"))
            def task_iris_pred():
                mod = pickle.load(open("/tmp/iris/variable_mod.pickle", "rb"))
                pred = iris_module.get_iris_pred(mod)
                pickle.dump(
                    pred, open("/tmp/iris/variable_pred.pickle", "wb")
                )
            with DAG(...) as dag:
                iris_model = PythonOperator(
                    task_id="iris_model_task",
                    python_callable=task_iris_model,
                )
                iris_pred = PythonOperator(
                    task_id="iris_pred_task",
                    python_callable=task_iris_pred,
                )
            iris_model >> iris_pred

        This way, the generated Airflow DAG file opens room for engineers
        to control pipeline runs at a finer level and allows for further customization.
        """

        DAG_TEMPLATE = load_plugin_template("airflow_dag_PythonOperator.jinja")

        if dag_flavor == AirflowDagFlavor.PythonOperatorPerSession:
            task_breakdown = DagTaskBreakdown.TaskPerSession
        elif dag_flavor == AirflowDagFlavor.PythonOperatorPerArtifact:
            task_breakdown = DagTaskBreakdown.TaskPerArtifact

        # Get task definitions based on dag_flavor
        task_defs, task_graph = get_task_graph(
            self.artifact_collection,
            pipeline_name=self.pipeline_name,
            task_breakdown=task_breakdown,
        )

        # Add setup and teardown if local pickle serializer is selected
        if task_serialization == TaskSerializer.LocalPickle:
            task_defs["setup"] = get_localpickle_setup_task_definition(
                self.pipeline_name
            )
            task_defs["teardown"] = get_localpickle_teardown_task_definition(
                self.pipeline_name
            )
            # insert in order to task_names so that setup runs first and teardown runs last
            task_graph.insert_setup_task("setup")
            task_graph.insert_teardown_task("teardown")

        rendered_task_defs = self.get_rendered_task_definitions(
            task_defs, task_serialization
        )

        task_dependencies = sorted(
            [f"{task0} >> {task1}" for task0, task1 in task_graph.graph.edges]
        )

        # Get DAG parameters for an Airflow pipeline
        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_pipeline_args().items():
            input_parameters_dict[parameter_name] = input_spec.value

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
            dag_params=input_parameters_dict,
            task_definitions=rendered_task_defs,
            tasks=task_defs,
            task_dependencies=task_dependencies,
        )

        return full_code

    def get_rendered_task_definitions(
        self,
        task_defs: Dict[str, TaskDefinition],
        task_serialization: TaskSerializer,
    ) -> List[str]:
        """
        Returns rendered tasks for the pipeline tasks.
        """
        TASK_FUNCTION_TEMPLATE = load_plugin_template(
            "task/task_function.jinja"
        )
        rendered_task_defs: List[str] = []
        for task_name, task_def in task_defs.items():
            loading_blocks, dumping_blocks = render_task_io_serialize_blocks(
                task_def, task_serialization
            )
            task_def_rendered = TASK_FUNCTION_TEMPLATE.render(
                function_name=task_name,
                user_input_variables=", ".join(task_def.user_input_variables),
                typing_blocks=task_def.typing_blocks,
                loading_blocks=loading_blocks,
                pre_call_block=task_def.pre_call_block,
                call_block=task_def.call_block,
                post_call_block=task_def.post_call_block,
                dumping_blocks=dumping_blocks,
                include_imports_locally=False,
            )
            rendered_task_defs.append(task_def_rendered)

        # sort here to maintain deterministic behavior of writing
        return sorted(rendered_task_defs)
