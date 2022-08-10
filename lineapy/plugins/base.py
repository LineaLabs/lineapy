import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from lineapy.api.api_utils import de_lineate_code
from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.program_slice import (
    CodeSlice,
    get_program_slice_by_artifact_name,
)
from lineapy.plugins.utils import get_lib_version_text, load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import get_system_python_version, prettify

logger = logging.getLogger(__name__)
configure_logging()


@dataclass
class BasePlugin:
    db: RelationalLineaDB
    session_id: LineaID

    def prepare_output_dir(self, copy_dst: str):
        """
        This helper creates directories if missing
        """
        if not os.path.exists(copy_dst):
            os.makedirs(copy_dst)

    def generate_python_module(
        self,
        module_name: str,
        artifacts_code: Dict[str, CodeSlice],
        output_dir_path: Path,
    ):
        """
        Generate python module code and save to a file.
        """
        full_import_block = ""
        full_code_block = ""
        for artifact_name, sliced_code in artifacts_code.items():
            _import_block = "\n".join(sliced_code.import_lines)
            _code_block = f"def {artifact_name}():\n\t" + "\n\t".join(
                sliced_code.body_lines
            )

            full_import_block += "\n" + _import_block
            full_code_block += "\n" + _code_block

        full_code = prettify(
            de_lineate_code(full_import_block + full_code_block, self.db)
        )
        (output_dir_path / f"{module_name}.py").write_text(full_code)
        logger.info(f"Generated python module {module_name}.py")

    def get_working_dir_as_str(self):
        working_directory = Path(
            self.db.get_session_context(self.session_id).working_directory
        )
        return str(working_directory.resolve())

    def generate_infra(
        self,
        module_name: str,
        output_dir_path: Path,
    ):
        """
        Generates templates to test the airflow module. Currently, we
        produce a <module_name>_Dockerfile and a <module_name>_requirements.txt file.
        These can be used to test the dag that gets generated by linea. For more
        details, :ref:`Testing locally <testingairflow>`
        """
        system_python_version = get_system_python_version()
        DOCKERFILE_TEMPLATE = load_plugin_template("dockerfile.jinja")
        dockerfile = DOCKERFILE_TEMPLATE.render(
            module_name=module_name, python_version=system_python_version
        )
        (output_dir_path / (module_name + "_Dockerfile")).write_text(
            dockerfile
        )
        logger.info(f"Generated Dockerfile {module_name}_Dockerfile")
        all_libs = self.db.get_libraries_for_session(self.session_id)
        lib_names_text = ""
        for lib in all_libs:
            lib_name = str(lib.package_name)
            if lib_name in sys.modules:
                text = get_lib_version_text(lib_name)
                lib_names_text += f"{text}\n"
        (output_dir_path / (module_name + "_requirements.txt")).write_text(
            lib_names_text
        )
        logger.info(
            f"Generated requirements file {module_name}_requirements.txt"
        )

    def slice_dag_helper(
        self,
        artifact_name_mapping: Dict[str, str],
        module_name: str,
        output_dir: Optional[str] = None,
    ) -> Path:
        """
        A generic function shared by Script and Airflow

        To create DAG from the sliced code. This includes a python
        file with one function per slice, task dependencies file in Airflow
        format and an example Dockerfile and requirements.txt that can be used
        to run this.

        :param slice_names: list of slice names to be used as tasks.
        :param module_name: name of the Python module the generated code will
            be saved to.
        :param output_dir: directory to save the generated code to.
        """

        artifacts_code = {}
        for slice_name, artifact_var in artifact_name_mapping.items():
            slice_code: CodeSlice = get_program_slice_by_artifact_name(
                self.db, slice_name, keep_lineapy_save=True
            )
            artifacts_code[artifact_var] = slice_code

        output_dir_path = Path.cwd()
        if output_dir:
            output_dir_path = Path(os.path.expanduser(output_dir))
            self.prepare_output_dir(
                copy_dst=str(output_dir_path.resolve()),
            )

        logger.info(
            "Pipeline source generated in the directory: %s", output_dir_path
        )
        self.generate_python_module(
            module_name, artifacts_code, output_dir_path
        )

        self.generate_infra(
            module_name=module_name, output_dir_path=output_dir_path
        )
        return output_dir_path
