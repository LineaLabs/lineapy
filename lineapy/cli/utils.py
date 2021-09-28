import os
from typing import Optional
from lineapy.utils import info_log
from tempfile import NamedTemporaryFile
from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.data.types import SessionType


def run_transformed(
    file_name: str,
    session_type: SessionType,
    execution_mode: ExecutionMode,
) -> None:
    transformer = Transformer()
    lines = open(file_name, "r").readlines()
    code = "".join(lines)

    transformer.transform(
        code,
        session_type=session_type,
        session_name=file_name,
        execution_mode=execution_mode,
    )

    # Write transformed code to a file and don't delete it, so
    # that if an exception is raised when executing it, we
    # can look at the traceback
    # transformed_code_file = NamedTemporaryFile(delete=False)
    # transformed_code_file.write(new_code.encode())
    # transformed_code_file.close()

    # info_log("new_code\n" + new_code)
    # bytecode = compile(new_code, transformed_code_file.name, "exec")

    # exec(bytecode)

    # Remove the file if we have no errors
    # os.unlink(transformed_code_file.name)
