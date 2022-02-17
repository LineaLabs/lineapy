from typing import List

from typing_extensions import TypedDict

from lineapy.plugins.base import BasePlugin

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
    def sliced_airflow_dag(
        self,
        slice_names: List[str],
        airflow_task_dependencies: str,
    ) -> str:
        """
        Returns a an Airflow DAG of the sliced code.

        :param slice_names: list of slice names to be used as tasks.
        :param func_name: name of the DAG and corresponding functions and task prefixes,
        i.e. "sliced_housing_dag"
        :param airflow_task_dependencies: task dependencies in Airflow format,
        i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
        This translates to "sliced_housing_dag_p >> sliced_housing_dag_y"
        and "sliced_housing_dag_p,sliced_housing_dag_x >> sliced_housing_dag_y".
        Here "sliced_housing_dag_p" and "sliced_housing_dag_x" are independent tasks
        and "sliced_housing_dag_y" depends on them.
        :return: string containing the code of the Airflow DAG running this slice
        """

        # Remove quotes
        airflow_task_dependencies = airflow_task_dependencies.replace(
            "\\'", ""
        )
        airflow_task_dependencies = airflow_task_dependencies.replace("'", "")

        artifacts_code = {}
        for slice_name in slice_names:
            artifact_var = self.tracer.artifact_var_name(slice_name)
            slice_code = self.tracer.slice(slice_name)
            artifacts_code[artifact_var] = slice_code
        self.generate_python_module(artifacts_code)
        # TODO self.generate_infra(airflow_task_dependencies)
