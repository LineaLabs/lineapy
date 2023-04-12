from lineapy.data.types import WorkflowType
from lineapy.plugins.airflow_workflow_writer import AirflowPipelineWriter
from lineapy.plugins.argo_workflow_writer import ARGOPipelineWriter
from lineapy.plugins.base_workflow_writer import BasePipelineWriter
from lineapy.plugins.dvc_workflow_writer import DVCPipelineWriter
from lineapy.plugins.kubeflow_workflow_writer import KubeflowPipelineWriter
from lineapy.plugins.ray_workflow_writer import RayPipelineWriter


class WorkflowWriterFactory:
    @classmethod
    def get(
        cls,
        workflow_type: WorkflowType = WorkflowType.SCRIPT,
        *args,
        **kwargs,
    ):
        if workflow_type == WorkflowType.AIRFLOW:
            return AirflowPipelineWriter(*args, **kwargs)
        elif workflow_type == WorkflowType.DVC:
            return DVCPipelineWriter(*args, **kwargs)
        elif workflow_type == WorkflowType.ARGO:
            return ARGOPipelineWriter(*args, **kwargs)
        elif workflow_type == WorkflowType.KUBEFLOW:
            return KubeflowPipelineWriter(*args, **kwargs)
        elif workflow_type == WorkflowType.RAY:
            return RayPipelineWriter(*args, **kwargs)
        else:
            return BasePipelineWriter(*args, **kwargs)
