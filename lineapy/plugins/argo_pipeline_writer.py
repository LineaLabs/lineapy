import base64
import errno
import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from kubernetes import client, config
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


class ARGODagFlavor(Enum):
    PythonOperatorPerSession = 1
    PythonOperatorPerArtifact = 2
    # KubernetesPodOperatorPerSession = 3
    # KubernetesPodOperatorPerArtifact = 4


ARGODAGConfig = TypedDict(
    "ARGODAGConfig",
    {
        "namespace": str,
        "host": str,
        "verify_ssl": str,
        "workflow_name": str,
        "service_account": int,
        "kube_config": str,
        "task_serialization": str,
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
                self.dag_config.get("dag_flavor", "PythonOperatorPerSession")
            ]
        except KeyError:
            raise ValueError(f'"{dag_flavor}" is an invalid ARGO dag flavor.')

        try:
            task_serialization = TaskSerializer[
                self.dag_config.get("task_serialization", "LocalPickleArgo")
            ]
        except KeyError:
            raise ValueError(
                f'"{task_serialization}" is an invalid type of task serialization scheme.'
            )

        # Construct DAG text for the given flavor
        full_code = self._write_operators(dag_flavor, task_serialization)

        print(full_code)

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(prettify(full_code))
        logger.info(f"Generated DAG file: {file}")

    def _write_operators(
        self,
        dag_flavor: ARGODagFlavor,
        task_serialization: TaskSerializer,
    ) -> str:

        DAG_TEMPLATE = load_plugin_template("argo_dag.jinja")

        if dag_flavor == ARGODagFlavor.PythonOperatorPerSession:
            task_breakdown = DagTaskBreakdown.TaskPerSession
        elif dag_flavor == ARGODagFlavor.PythonOperatorPerArtifact:
            task_breakdown = DagTaskBreakdown.TaskPerArtifact

        # Get task definitions based on dag_flavor
        task_defs, task_graph = get_task_graph(
            self.artifact_collection,
            pipeline_name=self.pipeline_name,
            task_breakdown=task_breakdown,
        )

        task_names = list(task_defs.keys())

        task_defs = {tn: task_defs[tn] for tn in task_names}

        rendered_task_defs = self.get_rendered_task_definitions(
            task_defs, task_serialization
        )

        # Handle dependencies
        dependencies = {
            task_names[i + 1]: {task_names[i]}
            for i in range(len(task_names) - 1)
        }

        task_dependencies = [
            f"{task0} >> {task1}" for task0, task1 in task_graph.graph.edges
        ]

        SERIALIZER_TEMPLATE = load_plugin_template(
            "task/localpickle/task_local_pickle_ser_argo.jinja"
        )

        return_artifacts = []
        for _, taskdef in task_defs.items():
            for return_variable in taskdef.return_vars:
                return_artifacts.append(return_variable)

        # Get DAG parameters for an ARGO pipeline
        input_parameters_dict: Dict[str, Any] = {}
        for parameter_name, input_spec in super().get_pipeline_args().items():
            input_parameters_dict[parameter_name] = input_spec.value

        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.pipeline_name,
            MODULE_NAME=self.pipeline_name + "_module",
            NAMESPACE=self.dag_config.get("namespace", "argo"),
            HOST=self.dag_config.get("host", "https://localhost:2746"),
            VERIFY_SSL=self.dag_config.get("verify_ssl", "False"),
            WORFLOW_NAME=self.dag_config.get(
                "workflow_name", self.pipeline_name.replace("_", "-")
            ),
            IMAGE=self.dag_config.get("image", "argo_pipeline:latest"),
            IMAGE_PULL_POLICY=self.dag_config.get(
                "image_pull_policy", "Never"
            ),
            TOKEN=self.get_sa_token(
                self.dag_config.get("service_account", "argo"),
                self.dag_config.get("namespace", "argo"),
                self.dag_config.get(
                    "kube_config", os.path.expanduser("~/.kube/config")
                ),
            ),
            dag_params=input_parameters_dict,
            task_definitions=rendered_task_defs,
            tasks=task_defs,
            task_dependencies=task_dependencies,
            return_artifacts=return_artifacts,
        )

        return full_code

    def get_rendered_task_definitions(
        self,
        task_defs: Dict[str, TaskDefinition],
        task_serialization: TaskSerializer,
    ) -> List[str]:
        """
        Returns rendered tasks for the pipeline tasks.
        """
        TASK_FUNCTION_TEMPLATE = load_plugin_template(
            "task/task_function_argo.jinja"
        )
        rendered_task_defs: List[str] = []
        for task_name, task_def in task_defs.items():
            loading_blocks, dumping_blocks = render_task_io_serialize_blocks(
                task_def, task_serialization
            )
            task_def_rendered = TASK_FUNCTION_TEMPLATE.render(
                imports=[
                    "import " + x
                    for x in [
                        self.pipeline_name + "_module",
                        "pickle",
                        "pathlib",
                    ]
                ],
                function_name=task_name,
                user_input_variables=", ".join(task_def.user_input_variables),
                typing_blocks=task_def.typing_blocks,
                loading_blocks=loading_blocks,
                call_block=task_def.call_block,
                dumping_blocks=dumping_blocks,
            )
            rendered_task_defs.append(task_def_rendered)

        return rendered_task_defs

    def get_sa_token(
        self,
        service_account: str,
        namespace: str = "argo",
        config_file: Optional[str] = None,
    ):
        if config_file is not None and not os.path.isfile(config_file):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), config_file
            )

        config.load_kube_config(config_file=config_file)
        v1 = client.CoreV1Api()
        print(
            "Getting service account token for service account: %s in namespace: %s"
            % (service_account, namespace)
        )

        if (
            v1.read_namespaced_service_account(
                service_account, namespace
            ).secrets
            is None
        ):
            print("No secrets found in namespace: %s" % namespace)
            return None

        secret_name = (
            v1.read_namespaced_service_account(service_account, namespace)
            .secrets[0]
            .name
        )

        sec = v1.read_namespaced_secret(secret_name, namespace).data
        return base64.b64decode(sec["token"]).decode()
