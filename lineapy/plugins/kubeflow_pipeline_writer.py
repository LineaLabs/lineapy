import logging
from enum import Enum
from typing import Dict, TypedDict

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.task import DagTaskBreakdown, TaskDefinition
from lineapy.plugins.taskgen import get_task_definitions
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class KubeflowDagFlavor(Enum):
    ComponentPerSession = 1
    ComponentPerArtifact = 2


KubeflowDagConfig = TypedDict(
    "KubeflowDagConfig",
    {
        "dag_flavor": str,  # Not native to DVC config
    },
    total=False,
)


class KubeflowPipelineWriter(BasePipelineWriter):
    def _write_dag(self) -> None:

        # Check if the given DAG flavor is a supported/valid one
        try:
            dag_flavor = KubeflowDagFlavor[
                self.dag_config.get("dag_flavor", "ComponentPerArtifact")
            ]
        except KeyError:
            raise ValueError(
                f'"{dag_flavor}" is an invalid kubeflow dag flavor.'
            )

        # Construct DAG text for the given flavor
        full_code = self._write_operators(dag_flavor)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(full_code)
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: KubeflowDagFlavor,
    ) -> str:
        """ """

        DAG_TEMPLATE = load_plugin_template("kubeflow_dag.jinja")

        if dag_flavor == KubeflowDagFlavor.ComponentPerSession:
            task_breakdown = DagTaskBreakdown.TaskPerSession
        elif dag_flavor == KubeflowDagFlavor.ComponentPerArtifact:
            task_breakdown = DagTaskBreakdown.TaskPerArtifact

        # Get task definitions based on dag_flavor
        task_defs: Dict[str, TaskDefinition] = get_task_definitions(
            self.artifact_collection,
            pipeline_name=self.pipeline_name,
            task_breakdown=task_breakdown,
        )

        task_names = list(task_defs.keys())

        task_defs = {tn: task_defs[tn] for tn in task_names}

        full_code = DAG_TEMPLATE.render()

        return full_code

    @property
    def docker_template_name(self) -> str:
        return "kubeflow_dockerfile.jinja"
