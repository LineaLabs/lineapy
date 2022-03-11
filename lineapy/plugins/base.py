from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import isort

from lineapy.instrumentation.tracer_context import TracerContext
from lineapy.utils.config import linea_folder
from lineapy.utils.utils import prettify


@dataclass
class BasePlugin:
    tracer_context: TracerContext

    def _split_code_blocks(self, code: str, func_name: str):
        """
        Split the list of code lines to import, main code and main func blocks.
        The code block is added under a function with given name.

        :param code: the source code to split.
        :param func_name: name of the function to create.
        :return: strings representing import_block, code_block, main_block.
        """
        # We split the lines in import and code blocks and join them to full code test
        lines = code.split("\n")
        # Imports are at the top, find where they end
        end_of_imports_line_num = 0
        import_open_bracket = False
        while (
            "import" in lines[end_of_imports_line_num]
            or "#" in lines[end_of_imports_line_num]
            or "" == lines[end_of_imports_line_num]
            or "    " in lines[end_of_imports_line_num]
            and import_open_bracket
            or ")" in lines[end_of_imports_line_num]
            and import_open_bracket
        ):
            if "(" in lines[end_of_imports_line_num]:
                import_open_bracket = True
            elif ")" in lines[end_of_imports_line_num]:
                import_open_bracket = False
            end_of_imports_line_num += 1
        # everything from here down needs to be under def()
        # TODO Support arguments to the func
        code_block = f"def {func_name}():\n\t" + "\n\t".join(
            lines[end_of_imports_line_num:]
        )
        import_block = "\n".join(lines[:end_of_imports_line_num])
        main_block = f"""if __name__ == "__main__":\n\tprint({func_name}())"""
        return import_block, code_block, main_block

    def generate_python_module(
        self,
        module_name: str,
        artifacts_code: Dict[str, str],
        output_dir: Optional[str] = None,
    ):
        """
        Generate python module code and save to a file.
        """
        full_import_block = ""
        full_code_block = ""
        for artifact_name, sliced_code in artifacts_code.items():
            _import_block, _code_block, _ = self._split_code_blocks(
                sliced_code, artifact_name
            )
            full_import_block += "\n" + _import_block
            full_code_block += "\n" + _code_block

        # Sort imports and move them to the top
        full_code = isort.code(
            full_import_block + full_code_block,
            float_to_top=True,
            profile="black",
        )
        full_code = prettify(full_code)
        output_dir_path = Path(output_dir) if output_dir else Path.cwd()
        (output_dir_path / f"{module_name}.py").write_text(full_code)

    def get_relative_working_dir_as_str(self):
        working_directory = Path(
            self.tracer_context.session_context.working_directory
        )
        return repr(
            str(
                working_directory.relative_to(
                    (linea_folder() / "..").resolve()
                )
            )
        )
