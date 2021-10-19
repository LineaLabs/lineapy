import logging
import os
import pathlib
import tempfile
from importlib import import_module

from black import FileMode, format_str

from lineapy.graph_reader.program_slice import (
    get_program_slice,
    split_code_blocks,
)
from lineapy.instrumentation.tracer import Tracer


def sliced_aiflow_dag(tracer: Tracer, slice_name: str, func_name: str) -> str:
    """
    Returns a an Airflow DAG of the sliced code.

    :param tracer: the tracer object.
    :param slice_name: name of the artifacts to get the code slice for.
    :return: string containing the code of the Airflow DAG running this slice
    """
    artifact = tracer.db.get_artifact_by_name(slice_name)
    artifact_var = tracer.slice_var_name(artifact)
    if not artifact_var:
        return "Unable to extract the slice"
    slice_code = get_program_slice(tracer.graph, [artifact.id])
    # We split the code in import and code blocks and join them to full code test
    import_block, code_block, main_block = split_code_blocks(
        slice_code, func_name
    )
    # TODO Add DAG specific blocks
    full_code = (
        import_block
        + "\n\n"
        + code_block
        + f"\n\treturn {artifact_var}"
        + "\n\n"
        + main_block
    )
    # Black lint
    black_mode = FileMode()
    black_mode.line_length = 79
    full_code = format_str(full_code, mode=black_mode)
    return full_code
