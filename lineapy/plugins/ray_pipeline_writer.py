import logging
from enum import Enum
from typing import Any, Dict, List

from typing_extensions import TypedDict

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.task import DagTaskBreakdown, TaskDefinition
from lineapy.plugins.taskgen import get_task_graph
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class RayDagFlavor(Enum):
    TaskPerSession = 1
    TaskPerArtifact = 2


RayDagConfig = TypedDict(
    "RayDagConfig",
    {
        "dag_flavor": str,  # Not native to RAY config
        "use_workflows": bool,
        "runtime_env": Dict,
        "storage": str,
    },
    total=False,
)


class RayPipelineWriter(BasePipelineWriter):
    def _write_dag(self) -> None:
        # Check if the given DAG flavor is a supported/valid one
        try:
            dag_flavor = RayDagFlavor[
                self.dag_config.get("dag_flavor", "TaskPerArtifact")
            ]
        except KeyError:
            raise ValueError(f'"{dag_flavor}" is an invalid ray dag flavor.')

        # Construct DAG text for the given flavor
        full_code = self._write_operators(dag_flavor)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(full_code)
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: RayDagFlavor,
    ) -> str:
        """
        Returns a code block containing all the operators for a Ray DAG.
        """

        if self.dag_config.get("use_workflows", True):
            DAG_TEMPLATE = load_plugin_template("ray_dag_workflow.jinja")
        else:
            DAG_TEMPLATE = load_plugin_template("ray_dag_remote.jinja")

        if dag_flavor == RayDagFlavor.TaskPerSession:
            task_breakdown = DagTaskBreakdown.TaskPerSession
        elif dag_flavor == RayDagFlavor.TaskPerArtifact:
            task_breakdown = DagTaskBreakdown.TaskPerArtifact

        # Get task definitions based on dag_flavor
        task_defs, task_graph = get_task_graph(
            self.artifact_collection,
            pipeline_name=self.pipeline_name,
            task_breakdown=task_breakdown,
        )

        if (
            self.dag_config.get("use_workflows", True)
            and len(task_graph.sink_nodes) > 1
        ):
            raise RuntimeError(
                "Ray workflows do not support multiple artifacts being returned as sink nodes.\n\
                Consider use use_workflows=False to disable using Ray Workflows API."
            )

        rendered_task_defs = self.get_rendered_task_definitions(task_defs)

        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_pipeline_args().items():
            input_parameters_dict[parameter_name] = input_spec.value

        # set ray working dir to local directory so that module file can be picked up
        # if this config is not already set
        ray_runtime_env = self.dag_config.get("runtime_env", {})
        if "working_dir" not in ray_runtime_env:
            ray_runtime_env["working_dir"] = "."

        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.pipeline_name,
            MODULE_NAME=self.pipeline_name + "_module",
            RAY_RUNTIME_ENV=ray_runtime_env,
            RAY_STORAGE=self.dag_config.get("storage", "/tmp"),
            task_definitions=rendered_task_defs,
            tasks=task_defs,
            dag_params=input_parameters_dict,
            # sink tasks needed for ray since DAG needs to specify them
            sink_tasks=task_graph.sink_nodes,
        )

        return prettify(full_code)

    @property
    def docker_template_name(self) -> str:
        return "ray_dockerfile.jinja"

    def get_rendered_task_definitions(
        self,
        task_defs: Dict[str, TaskDefinition],
    ) -> List[str]:
        """
        Returns rendered tasks for the pipeline tasks along with a dictionary to lookup
        previous task outputs.

        The returned dictionary is used by the DAG to connect the right input files to
        output files for inter task communication.
        """

        TASK_FUNCTION_TEMPLATE = load_plugin_template(
            "task/task_function.jinja"
        )
        rendered_task_defs: List[str] = []

        for task_name, task_def in task_defs.items():

            input_vars = (
                task_def.user_input_variables + task_def.loaded_input_variables
            )

            # only specify num returns in function decorator for worflow
            function_decorator = "@ray.remote"
            if not self.dag_config.get("use_workflows", True):
                function_decorator += (
                    f"(num_returns={len(task_def.return_vars)})"
                )
            elif len(task_def.return_vars) > 1:
                raise RuntimeError(
                    f"Ray workflows do not support tasks with multiple returns. Task {task_name} has {len(task_def.return_vars)} returns.\n\
                    Consider use use_workflows=False to disable using Ray Workflows API."
                )

            task_def_rendered = TASK_FUNCTION_TEMPLATE.render(
                function_decorator=function_decorator,
                function_name=task_name,
                user_input_variables=", ".join(input_vars),
                typing_blocks=task_def.typing_blocks,
                pre_call_block="",
                call_block=task_def.call_block,
                post_call_block=task_def.post_call_block,
                return_block=f"return {', '.join(task_def.return_vars)}",
            )
            rendered_task_defs.append(task_def_rendered)

        return rendered_task_defs
