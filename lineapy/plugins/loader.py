import importlib.util
import sys
import tempfile
from importlib.abc import Loader
from pathlib import Path

from lineapy.plugins.base_pipeline_writer import BasePipelineWriter
from lineapy.utils.utils import prettify


def load_as_module(writer: BasePipelineWriter):
    """
    Writing module text to a temp file and load module with names of
    ``session_art1_art2_...```
    """

    module_name = f"session_{'_'.join(writer.artifact_collection.session_artifacts.keys())}"
    temp_folder = tempfile.mkdtemp()
    temp_module_path = Path(temp_folder, f"{module_name}.py")

    with open(temp_module_path, "w") as f:
        f.writelines(prettify(writer._compose_module()))

    spec = importlib.util.spec_from_file_location(
        module_name, temp_module_path
    )
    if spec is not None:
        session_module = importlib.util.module_from_spec(spec)
        assert isinstance(spec.loader, Loader)
        sys.modules["module.name"] = session_module
        spec.loader.exec_module(session_module)
        return session_module
    else:
        raise Exception("LineaPy cannot retrive a module.")
