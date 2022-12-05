from lineapy.data.types import PipelineType
from lineapy.plugins.airflow_pipeline_writer import AirflowPipelineWriter
from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.plugins.dvc_pipeline_writer import DVCPipelineWriter


class PipelineWriterFactory:
    @classmethod
    def get(
        cls,
        pipeline_type: PipelineType = PipelineType.SCRIPT,
        *args,
        **kwargs,
    ):
        if pipeline_type == PipelineType.AIRFLOW:
            return AirflowPipelineWriter(*args, **kwargs)
        elif pipeline_type == PipelineType.DVC:
            return DVCPipelineWriter(*args, **kwargs)
        else:
            return BasePipelineWriter(*args, **kwargs)
