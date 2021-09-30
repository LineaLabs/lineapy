import os
from typing import Optional
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils import info_log
from tempfile import NamedTemporaryFile
from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.data.types import SessionType


def run_transformed(
    file_name: str,
    session_type: SessionType,
    execution_mode: ExecutionMode,
) -> Tracer:
    transformer = Transformer()
    lines = open(file_name, "r").readlines()
    code = "".join(lines)

    transformer.transform(
        code,
        session_type=session_type,
        session_name=file_name,
        execution_mode=execution_mode,
    )
    return transformer.tracer
