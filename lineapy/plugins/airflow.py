import logging
from pathlib import Path
from typing import List, Optional

import isort
from typing_extensions import TypedDict

from lineapy.plugins.base import BasePlugin
from lineapy.plugins.task import TaskGraph, TaskGraphEdge
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


AirflowDagConfig = TypedDict(
    "AirflowDagConfig",
    {
        "owner": str,
        "retries": int,
        "start_date": str,
        "schedule_interval": str,
        "max_active_runs": int,
        "catchup": str,
    },
    total=False,
)


class AirflowPlugin(BasePlugin):
    def to_airflow(
        self,
        dag_name: str,
        task_names: List[str],
        output_dir_path: Path,
        task_graph: TaskGraph,
        airflow_dag_config: Optional[AirflowDagConfig] = {},
    ) -> None:
        """
        Create an Airflow DAG.

        :param dag_name: Name of the DAG and the python file it is saved in
        :param task_dependencies: Tasks dependencies in graphlib format
            {'B':{'A','C'}}"; this means task A and C are prerequisites for
            task B.
        :param airflow_dag_config: Configs of Airflow DAG model. See
            https://airflow.apache.org/_api/airflow/models/dag/index.html#airflow.models.dag.DAG
            for the full spec.
        """

        AIRFLOW_DAG_TEMPLATE = load_plugin_template("airflow_dag.jinja")
        airflow_dag_config = airflow_dag_config or {}

        full_code = AIRFLOW_DAG_TEMPLATE.render(
            DAG_NAME=dag_name,
            OWNER=airflow_dag_config.get("owner", "airflow"),
            RETRIES=airflow_dag_config.get("retries", 2),
            START_DATE=airflow_dag_config.get("start_date", "days_ago(1)"),
            SCHEDULE_IMTERVAL=airflow_dag_config.get(
                "schedule_interval", "*/15 * * * *"
            ),
            MAX_ACTIVE_RUNS=airflow_dag_config.get("max_active_runs", 1),
            CATCHUP=airflow_dag_config.get("catchup", "False"),
            tasks=task_names,
            task_dependencies=task_graph.get_airflow_dependency(),
        )
        # Sort imports and move them to the top
        full_code = isort.code(full_code, float_to_top=True, profile="black")
        full_code = prettify(full_code)
        (output_dir_path / f"{dag_name}_dag.py").write_text(full_code)
        logger.info(
            f"Added Airflow DAG named {dag_name}_dag. Start a run from the Airflow UI or CLI."
        )

    def sliced_airflow_dag(
        self,
        slice_names: List[str],
        module_name: Optional[str] = None,
        task_dependencies: TaskGraphEdge = {},
        output_dir: Optional[str] = None,
        airflow_dag_config: Optional[AirflowDagConfig] = {},
    ):
        (
            module_name,
            artifact_safe_names,
            output_dir_path,
            task_graph,
        ) = self.slice_dag_helper(
            slice_names, module_name, task_dependencies, output_dir
        )
        self.to_airflow(
            module_name,
            artifact_safe_names,
            output_dir_path,
            task_graph,
            airflow_dag_config,
        )
        return output_dir_path
