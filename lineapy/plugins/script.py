import logging
from pathlib import Path
from typing import Optional

from typing_extensions import TypedDict

from lineapy.plugins.base import BasePlugin
from lineapy.plugins.task import TaskGraph
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

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
        output_dir_path: Path,
        task_graph: TaskGraph,
    ) -> None:
        """
        Create an Python Script DAG.

        :param dag_name: Name of the DAG and the python file it is saved in
        :param output_dir_path: Directory of the DAG and the python file it is saved in
        :param task_graph:
        """

        SCRIPT_DAG_TEMPLATE = load_plugin_template("script_dag.jinja")
        full_code = SCRIPT_DAG_TEMPLATE.render(
            DAG_NAME=dag_name,
            tasks=task_graph.get_taskorder(),
        )
        full_code = prettify(full_code)
        (output_dir_path / f"{dag_name}_script_dag.py").write_text(full_code)
        logger.info(
            f"Added Python Script DAG named {dag_name}_script_dag.py. Start a run from the CLI."
        )

    def sliced_pipeline_dag(
        self,
        module_name: str,
        task_graph: TaskGraph,
        output_dir: Optional[str] = None,
    ):
        output_dir_path = self.slice_dag_helper(
            task_graph.artifact_raw_to_safe_mapping,
            module_name,
            output_dir,
        )
        self.to_script(
            module_name,
            output_dir_path,
            task_graph,
        )
        return output_dir_path
