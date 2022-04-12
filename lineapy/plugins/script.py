import logging
import os
from pathlib import Path
from typing import List, Optional

import isort
from typing_extensions import TypedDict

from lineapy.graph_reader.program_slice import (
    get_program_slice_by_artifact_name,
)
from lineapy.plugins.base import BasePlugin
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

from .utils import load_plugin_template, safe_var_name

logger = logging.getLogger(__name__)
configure_logging()


ScriptDagConfig = TypedDict(
    "ScriptDagConfig",
    {},
    total=False,
)


class ScriptPlugin(BasePlugin):
    def to_script(
        self,
        dag_name: str,
        task_names: List[str],
        output_dir_path: Path,
        task_dependencies: Optional[str] = None,
    ) -> None:
        """
        Create an Python Script DAG.

        :param dag_name: Name of the DAG and the python file it is saved in
        :param task_names:
        :param output_dir_path: Directory of the DAG and the python file it is saved in
        :param task_dependencies: task dependencies in an Airflow format,
                                            i.e. "p_value >> y" and "p_value, x >> y".
                                            Here "p_value" and "x" are independent tasks
                                            and "y" depends on them.
        """

        SCRIPT_DAG_TEMPLATE = load_plugin_template("script_dag.jinja")

        full_code = SCRIPT_DAG_TEMPLATE.render(
            DAG_NAME=dag_name,
            tasks=task_names,
            task_dependencies=task_dependencies,
        )
        # Sort imports and move them to the top
        full_code = isort.code(full_code, float_to_top=True, profile="black")
        full_code = prettify(full_code)
        (output_dir_path / f"{dag_name}_script_dag.py").write_text(full_code)
        logger.info(
            f"Added Python Script DAG named {dag_name}_script_dag. Start a run from the CLI."
        )

    def sliced_pipeline_dag(
        self,
        slice_names: List[str],
        module_name: Optional[str] = None,
        task_dependencies: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Creates an Python Script DAG from the sliced code. This includes a python file with one function per slice,
        an example Dockerfile and requirements.txt that can be used to run this.

        :param slice_names: list of slice names to be used as tasks.
        :param module_name: name of the Pyhon module the generated code will be saved to.
        :param task_dependencies: task dependencies in an artifact format,
                                            i.e. "'p value' >> 'y'" or "'p value', 'x' >> 'y'". Put slice names under single quotes.
                                            This translates to "p_value >> y" and "p_value, x >> y" when converting to Airflow.
        :param output_dir: directory to save the generated code to.
        """

        # Remove quotes
        if task_dependencies:
            task_dependencies = task_dependencies.replace("\\'", "")
            task_dependencies = task_dependencies.replace("'", "")

        artifacts_code = {}
        task_names = []
        for slice_name in slice_names:
            artifact_var = safe_var_name(slice_name)
            slice_code = get_program_slice_by_artifact_name(
                self.db, slice_name
            )
            artifacts_code[artifact_var] = slice_code
            task_name = f"{artifact_var}"
            task_names.append(task_name)
            # "'p value' >> 'y'" gets replaced by "p_value >> y"
            if task_dependencies:
                task_dependencies = task_dependencies.replace(
                    slice_name, task_name
                )
        module_name = module_name or "_".join(slice_names)
        output_dir_path = Path.cwd()
        if output_dir:
            output_dir_path = Path(os.path.expanduser(output_dir))
            self.prepare_output_dir(
                copy_dst=str(output_dir_path.resolve()),
            )

        logger.info(
            "Pipeline source generated in the directory: %s", output_dir_path
        )
        self.generate_python_module(
            module_name, artifacts_code, output_dir_path
        )
        self.to_script(
            module_name,
            task_names,
            output_dir_path,
            task_dependencies,
            # airflow_dag_config,
        )
        self.generate_infra(
            module_name=module_name, output_dir_path=output_dir_path
        )
        return output_dir_path
