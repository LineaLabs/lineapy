from lineapy.instrumentation.tracer import Tracer
from lineapy.utils import info_log
from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.data.types import SessionType


def run_transformed(
    file_name: str,
    session_type: SessionType,
    execution_mode: ExecutionMode,
    print_source: bool = False,
) -> Tracer:
    transformer = Transformer()
    lines = open(file_name, "r").readlines()
    code = "".join(lines)
    if print_source:
        print("Running Linea on source:")
        print(code)
    transformer.transform(
        code,
        session_type=session_type,
        session_name=file_name,
        execution_mode=execution_mode,
    )
    return transformer.tracer
