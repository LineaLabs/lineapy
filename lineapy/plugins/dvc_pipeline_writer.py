import logging
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel
from typing_extensions import TypedDict

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.task import (
    DagTaskBreakdown,
    TaskDefinition,
    TaskSerializer,
    render_task_io_serialize_blocks,
)
from lineapy.plugins.taskgen import get_task_graph
from lineapy.plugins.utils import load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


class Stage(BaseModel):
    name: str
    deps: List[str]
    outs: List[str]
    call_block: str
    user_input_variables: Dict[str, Any]


class DVCDagFlavor(Enum):
    SingleStageAllSessions = 1
    StagePerArtifact = 2
    # TODO: StagePerSession


DVCDagConfig = TypedDict(
    "DVCDagConfig",
    {
        "dag_flavor": str,  # Not native to DVC config
    },
    total=False,
)


class DVCPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "DVC" framework.
    """

    @property
    def docker_template_name(self) -> str:
        return "dvc/dvc_dockerfile.jinja"

    def _write_dag(self) -> None:
        dag_flavor = self.dag_config.get("dag_flavor", "StagePerArtifact")

        # Check if the given DAG flavor is a supported/valid one
        if dag_flavor not in DVCDagFlavor.__members__:
            raise ValueError(f'"{dag_flavor}" is an invalid dvc dag flavor.')

        # Construct DAG text for the given flavor
        if DVCDagFlavor[dag_flavor] == DVCDagFlavor.SingleStageAllSessions:
            dvc_yaml_code = self._write_operator_run_all_sessions()

        if DVCDagFlavor[dag_flavor] == DVCDagFlavor.StagePerArtifact:
            dvc_yaml_code = self._write_operator_run_per_artifact()

        # Write out file
        dvc_dag_file = self.output_dir / "dvc.yaml"
        dvc_dag_file.write_text(dvc_yaml_code)
        logger.info(f"Generated DAG file: {dvc_dag_file}")

    def _write_operator_run_all_sessions(self) -> str:
        """
        This hidden method implements DVC DAG code generation corresponding
        to the `SingleStageAllSessions` flavor. This DAG only has one stage and
        calls `run_all_sessions` generated by the module file.
        """

        DAG_TEMPLATE = load_plugin_template(
            "dvc/dvc_dag_SingleStageAllSessions.jinja"
        )

        full_code = DAG_TEMPLATE.render(
            MODULE_COMMAND=f"python {self.pipeline_name}_module.py",
        )

        return full_code

    def _write_operator_run_per_artifact(self) -> str:
        """
        This hidden method implements DVC DAG code generation corresponding
        to the `StagePerArtifact` flavor.
        """

        DAG_TEMPLATE = load_plugin_template(
            "dvc/dvc_dag_StagePerArtifact.jinja"
        )

        task_defs, _ = get_task_graph(
            self.artifact_collection,
            pipeline_name=self.pipeline_name,
            task_breakdown=DagTaskBreakdown.TaskPerArtifact,
        )

        full_code = DAG_TEMPLATE.render(
            MODULE_NAME=f"{self.pipeline_name}_module", TASK_DEFS=task_defs
        )

        self._write_params()

        for task_name, task_def in task_defs.items():
            self._write_python_operator_per_run_artifact(task_name, task_def)

        return full_code

    def _write_params(self):
        # Get DAG parameters for an DVC pipeline
        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_pipeline_args().items():
            input_parameters_dict[parameter_name] = input_spec.value

        PARAMS_TEMPLATE = load_plugin_template("dvc/dvc_dag_params.jinja")

        params_code = PARAMS_TEMPLATE.render(
            input_parameters_dict=input_parameters_dict
        )
        filename = "params.yaml"
        params_file = self.output_dir / filename
        params_file.write_text(params_code)
        logger.info(f"Generated DAG file: {params_file}")

    def _write_python_operator_per_run_artifact(
        self, task_name: str, task_def: TaskDefinition
    ):
        """
        This hidden method generates the python cmd files for each DVC stage.
        """
        TASK_TEMPLATE = load_plugin_template("task/task_function.jinja")

        STAGE_TEMPLATE = load_plugin_template(
            "dvc/dvc_dag_PythonOperator.jinja"
        )

        loading_blocks, dumping_blocks = render_task_io_serialize_blocks(
            task_def, TaskSerializer.CWDPickle
        )

        python_operator_code = TASK_TEMPLATE.render(
            function_name=task_name,
            user_input_variables=", ".join(task_def.user_input_variables),
            typing_blocks=task_def.typing_blocks,
            loading_blocks=loading_blocks,
            pre_call_block=task_def.pre_call_block,
            call_block=task_def.call_block,
            post_call_block=task_def.post_call_block,
            dumping_blocks=dumping_blocks,
            return_block="",
            include_imports_locally=False,
        )

        stage_code = STAGE_TEMPLATE.render(
            MODULE_NAME=f"{self.pipeline_name}_module",
            TASK_CODE=python_operator_code,
            task_name=task_name,
            # DVC tasks read each input variable and cannot rely on DAG to provide them
            # provide a list here for the main function body
            task_parameters=task_def.user_input_variables,
        )

        filename = f"task_{task_name}.py"
        python_operator_file = self.output_dir / filename
        python_operator_file.write_text(prettify(stage_code))
        logger.info(f"Generated DAG file: {python_operator_file}")
