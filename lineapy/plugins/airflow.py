import ast
from pathlib import Path
from typing import List, Optional

import isort
from typing_extensions import TypedDict

from lineapy.plugins.base import BasePlugin
from lineapy.utils.utils import prettify

from .utils import load_plugin_template

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


def split_code_blocks(code: str, func_name: str):
    """
    Split the list of code lines to import, main code and main func blocks.
    The code block is added under a function with given name.

    :param code: the source code to split.
    :param func_name: name of the function to create.
    :return: strings representing import_block, code_block, main_block.
    """
    # We split the lines in import and code blocks and join them to full code test
    lines = code.split("\n")
    ast_tree = ast.parse(code)
    # Imports are at the top, find where they end
    end_of_imports_line_num = 0
    for node in ast_tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        else:
            end_of_imports_line_num = node.lineno - 1
            break

    # TODO Support arguments to the func
    code_block = f"def {func_name}():\n\t" + "\n\t".join(
        lines[end_of_imports_line_num:]
    )
    import_block = "\n".join(lines[:end_of_imports_line_num])
    main_block = f"""if __name__ == "__main__":\n\tprint({func_name}())"""
    return import_block, code_block, main_block


class AirflowPlugin(BasePlugin):
    def to_airflow(
        self,
        dag_name: str,
        task_names: List[str],
        task_dependencies: Optional[str] = None,
        output_dir: Optional[str] = None,
        airflow_dag_config: AirflowDagConfig = {},
    ) -> None:
        """
        Create an Airflow DAG.

        :param dag_name: Name of the DAG and the python file it is saved in
        :param airflow_task_dependencies: task dependencies in an Airflow format,
                                            i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
                                            This translates to "sliced_housing_dag_p >> sliced_housing_dag_y"
                                            and "sliced_housing_dag_p,sliced_housing_dag_x >> sliced_housing_dag_y".
                                            Here "sliced_housing_dag_p" and "sliced_housing_dag_x" are independent tasks
                                            and "sliced_housing_dag_y" depends on them.
        :param airflow_dag_config: Configs of Airflow DAG model. See
            https://airflow.apache.org/_api/airflow/models/dag/index.html#airflow.models.dag.DAG
            for the full spec.
        """

        AIRFLOW_DAG_TEMPLATE = load_plugin_template("airflow_dag.jinja")
        airflow_dag_config = airflow_dag_config or {}

        full_code = AIRFLOW_DAG_TEMPLATE.render(
            working_dir_str=self.get_relative_working_dir_as_str(),
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
            task_dependencies=task_dependencies,
        )
        # Sort imports and move them to the top
        full_code = isort.code(full_code, float_to_top=True, profile="black")
        full_code = prettify(full_code)
        output_dir_path = Path(output_dir) if output_dir else Path.cwd()
        (output_dir_path / f"{dag_name}_dag.py").write_text(full_code)

    def sliced_airflow_dag(
        self,
        slice_names: List[str],
        module_name: str,
        airflow_task_dependencies: Optional[str] = None,
        output_dir: Optional[str] = None,
        airflow_dag_config: AirflowDagConfig = {},
    ):
        """
        Creates an Airflow DAG from the sliced code. This includes a python file with one function per slice, task dependencies
        file in Airflow format and an example Dockerfile and requirements.txt that can be used to run this.

        :param slice_names: list of slice names to be used as tasks.
        :param module_name: name of the Pyhon module the generated code will be saved to.
        :param airflow_task_dependencies: task dependencies in an Airflow format,
                                            i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
                                            This translates to "sliced_housing_dag_p >> sliced_housing_dag_y"
                                            and "sliced_housing_dag_p,sliced_housing_dag_x >> sliced_housing_dag_y".
                                            Here "sliced_housing_dag_p" and "sliced_housing_dag_x" are independent tasks
                                            and "sliced_housing_dag_y" depends on them.
        """

        # Remove quotes
        if airflow_task_dependencies:
            airflow_task_dependencies = airflow_task_dependencies.replace(
                "\\'", ""
            )
            airflow_task_dependencies = airflow_task_dependencies.replace(
                "'", ""
            )

        artifacts_code = {}
        task_names = []
        for slice_name in slice_names:
            # the or part handles lineapy.db or lineapy.filesystem types of artifacts
            artifact_var = (
                self.tracer_context.artifact_var_name(slice_name) or slice_name
            )
            slice_code = self.tracer_context.slice(slice_name)
            artifacts_code[artifact_var] = slice_code
            # "'p value' >> 'y'" needs to be replaced by "sliced_housing_dag_p >> sliced_housing_dag_y"
            task_name = f"{artifact_var}"
            task_names.append(task_name)
            if airflow_task_dependencies:
                airflow_task_dependencies = airflow_task_dependencies.replace(
                    slice_name, task_name
                )
        self.generate_python_module(module_name, artifacts_code, output_dir)
        self.to_airflow(
            module_name,
            task_names,
            airflow_task_dependencies,
            output_dir,
            airflow_dag_config,
        )
