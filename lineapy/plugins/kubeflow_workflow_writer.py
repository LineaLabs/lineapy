import logging
from enum import Enum
from typing import Any, Dict, List

from typing_extensions import TypedDict

from lineapy.plugins.base_workflow_writer import BasePipelineWriter
from lineapy.plugins.task import (
    DagTaskBreakdown,
    TaskDefinition,
    TaskSerializer,
    render_task_definitions,
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


class KubeflowDagFlavor(Enum):
    ComponentPerSession = 1
    ComponentPerArtifact = 2


KubeflowDagConfig = TypedDict(
    "KubeflowDagConfig",
    {
        "host_url": str,
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
        file = self.output_dir / f"{self.workflow_name}_dag.py"
        file.write_text(full_code)
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: KubeflowDagFlavor,
    ) -> str:
        """
        Returns a code block containing all the operators for a Kubeflow DAG.
        """

        DAG_TEMPLATE = load_plugin_template("kubeflow/kubeflow_dag.jinja")

        if dag_flavor == KubeflowDagFlavor.ComponentPerSession:
            task_breakdown = DagTaskBreakdown.TaskPerSession
        elif dag_flavor == KubeflowDagFlavor.ComponentPerArtifact:
            task_breakdown = DagTaskBreakdown.TaskPerArtifact

        # Get task definitions based on dag_flavor
        task_defs, task_graph = get_task_graph(
            self.artifact_collection,
            workflow_name=self.workflow_name,
            task_breakdown=task_breakdown,
        )

        task_defs["setup"] = get_noop_setup_task_definition(self.workflow_name)
        task_defs["teardown"] = get_noop_teardown_task_definition(
            self.workflow_name
        )
        # insert in order to task_names so that setup runs first and teardown runs last
        task_graph.insert_setup_task("setup")
        task_graph.insert_teardown_task("teardown")

        task_names = list(task_defs.keys())
        task_defs = {tn: task_defs[tn] for tn in task_names}

        rendered_task_defs = self.get_rendered_task_definitions(task_defs)
        task_loading_blocks = self.get_task_input_loading_code_blocks(
            task_defs
        )

        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_workflow_args().items():
            input_parameters_dict[parameter_name] = input_spec.value

        task_dependencies = sorted(
            [
                f"task_{task1}.after(task_{task0})"
                for task0, task1 in task_graph.graph.edges
            ]
        )

        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.workflow_name,
            HOST_URL=self.dag_config.get("host_url", "http://localhost:3000"),
            dag_params=input_parameters_dict,
            task_definitions=rendered_task_defs,
            tasks=task_defs,
            task_loading_blocks=task_loading_blocks,
            task_dependencies=task_dependencies,
        )

        return prettify(full_code)

    @property
    def docker_template_name(self) -> str:
        return "kubeflow/kubeflow_dockerfile.jinja"

    def get_task_input_loading_code_blocks(self, task_defs) -> Dict[str, str]:
        """
        Returns a dictionary to lookup previous task outputs.

        The returned dictionary is used by the DAG to connect the right input files to
        output files for inter task communication.
        """
        task_input_loading_code_blocks: Dict[str, str] = {}

        for task_name, task_def in task_defs.items():
            # this task will output variables to a file that other tasks can access
            # through KFP's task.outputs attribute
            for return_variable in task_def.return_vars:
                task_input_loading_code_blocks[
                    return_variable
                ] = f'task_{task_name}.outputs["variable_{return_variable}"]'
        return task_input_loading_code_blocks

    def get_rendered_task_definitions(
        self,
        task_defs: Dict[str, TaskDefinition],
    ) -> List[str]:
        """
        Returns rendered tasks for the pipeline tasks
        """

        def user_input_variables_fn(task_def) -> str:

            input_vars = task_def.user_input_variables

            input_paths = [
                f"variable_{loaded_input_variable}_path: kfp.components.InputPath(str)"
                for loaded_input_variable in task_def.loaded_input_variables
            ]

            output_paths = [
                f"variable_{return_variable}_path: kfp.components.OutputPath(str)"
                for return_variable in task_def.return_vars
            ]

            return ", ".join(input_vars + input_paths + output_paths)

        rendered_task_defs: List[str] = render_task_definitions(
            task_defs,
            self.workflow_name,
            task_serialization=TaskSerializer.ParametrizedPickle,
            user_input_variables_fn=user_input_variables_fn,
            include_imports_locally=True,
        )

        return rendered_task_defs
