import logging
from enum import Enum
from typing import Any, Dict, List, Tuple

from typing_extensions import TypedDict

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.task import (
    DagTaskBreakdown,
    TaskDefinition,
    TaskSerializer,
    render_task_io_serialize_blocks,
)
from lineapy.plugins.taskgen import (
    get_noop_setup_task_definition,
    get_noop_teardown_task_definition,
    get_task_graph,
)
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class ARGODagFlavor(Enum):
    StepPerSession = 1


ARGODAGConfig = TypedDict(
    "ARGODAGConfig",
    {
        "namespace": str,
        "host": str,
        "verify_ssl": str,
        "image": str,
        "image_pull_policy": str,
        "token": str,
        "workflow_name": str,
        "service_account": int,
        "kube_config": str,
        "dag_flavor": str,
    },
    total=False,
)


class ARGOPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "ARGO" framework.
    """

    @property
    def docker_template_name(self) -> str:
        return "argo_dockerfile.jinja"

    def _write_dag(self) -> None:

        # Check if the given DAG flavor is a supported/valid one
        try:
            dag_flavor = ARGODagFlavor[
                self.dag_config.get("dag_flavor", "StepPerSession")
            ]
        except KeyError:
            raise ValueError(f'"{dag_flavor}" is an invalid ARGO dag flavor.')

        # Construct DAG text for the given flavor
        full_code = self._write_operators(dag_flavor)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(prettify(full_code))
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: ARGODagFlavor,
    ) -> str:

        DAG_TEMPLATE = load_plugin_template("argo_dag.jinja")

        if dag_flavor == ARGODagFlavor.StepPerSession:
            task_breakdown = DagTaskBreakdown.TaskPerSession

        # Get task definitions based on dag_flavor
        task_defs, task_graph = get_task_graph(
            self.artifact_collection,
            pipeline_name=self.pipeline_name,
            task_breakdown=task_breakdown,
        )

        task_defs["setup"] = get_noop_setup_task_definition(self.pipeline_name)
        task_defs["teardown"] = get_noop_teardown_task_definition(
            self.pipeline_name
        )
        # insert in order to task_names so that setup runs first and teardown runs last
        task_graph.insert_setup_task("setup")
        task_graph.insert_teardown_task("teardown")

        task_names = list(task_defs.keys())

        task_defs = {tn: task_defs[tn] for tn in task_names}

        (
            rendered_task_defs,
            task_loading_blocks,
        ) = self.get_rendered_task_definitions(task_defs)

        # Handle dependencies
        task_dependencies = reversed(
            [f"{task0} >> {task1}" for task0, task1 in task_graph.graph.edges]
        )

        # Get DAG parameters for an ARGO pipeline
        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_pipeline_args().items():
            input_parameters_dict[parameter_name] = input_spec.value

        # set kube config to be user given path or expand default ~/.kube/config
        if "kube_config" in self.dag_config:
            kube_config = f'"{self.dag_config.get("kube_config")}"'
        else:
            kube_config = 'os.path.expanduser("~/.kube/config")'

        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.pipeline_name,
            MODULE_NAME=self.pipeline_name + "_module",
            NAMESPACE=self.dag_config.get("namespace", "argo"),
            HOST=self.dag_config.get("host", "https://localhost:2746"),
            VERIFY_SSL=self.dag_config.get("verify_ssl", "False"),
            WORFLOW_NAME=self.dag_config.get(
                "workflow_name", self.pipeline_name.replace("_", "-")
            ),
            IMAGE=self.dag_config.get(
                "image", f"{self.pipeline_name}:lineapy"
            ),
            IMAGE_PULL_POLICY=self.dag_config.get(
                "image_pull_policy", "Never"
            ),
            SERVICE_ACCOUNT=self.dag_config.get("service_account", "argo"),
            KUBE_CONFIG_PATH_CODE_BLOCK=kube_config,
            TOKEN=self.dag_config.get("token", "None"),
            dag_params=input_parameters_dict,
            task_definitions=rendered_task_defs,
            tasks=task_defs,
            task_loading_blocks=task_loading_blocks,
            task_dependencies=task_dependencies,
        )

        return full_code

    def get_rendered_task_definitions(
        self,
        task_defs: Dict[str, TaskDefinition],
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Returns rendered tasks for the pipeline tasks along with a dictionary to lookup
        previous task outputs.
        The returned dictionary is used by the DAG to connect the right input files to
        output files for inter task communication.
        This method originates from:
        https://github.com/argoproj-labs/hera-workflows/blob/4efddc85bfce62455db758f4be47e3acc0342b4f/examples/k8s_sa.py#L12
        """
        TASK_FUNCTION_TEMPLATE = load_plugin_template(
            "task/task_function.jinja"
        )
        rendered_task_defs: List[str] = []
        task_loading_blocks: Dict[str, str] = {}

        for task_name, task_def in task_defs.items():
            loading_blocks, dumping_blocks = render_task_io_serialize_blocks(
                task_def, TaskSerializer.LocalPickle
            )

            input_vars = task_def.user_input_variables

            # this task will output variables to a file that other tasks can access

            for return_variable in task_def.return_vars:
                task_loading_blocks[return_variable] = return_variable

            task_def_rendered = TASK_FUNCTION_TEMPLATE.render(
                MODULE_NAME=self.pipeline_name + "_module",
                function_name=task_name,
                user_input_variables=", ".join(input_vars),
                typing_blocks=task_def.typing_blocks,
                loading_blocks=loading_blocks,
                pre_call_block=task_def.pre_call_block or "",
                call_block=task_def.call_block,
                post_call_block=task_def.post_call_block or "",
                dumping_blocks=dumping_blocks,
                include_imports_locally=True,
                return_block="",
            )
            rendered_task_defs.append(task_def_rendered)

        return rendered_task_defs, task_loading_blocks
