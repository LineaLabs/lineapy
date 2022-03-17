import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import isort

from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.utils.config import linea_folder
from lineapy.utils.utils import prettify


@dataclass
class BasePlugin:
    db: RelationalLineaDB
    session_id: LineaID

    def split_code_blocks(self, code: str, func_name: str):
        """
        Split the list of code lines to import, main code and main func blocks.
        The code block is added under a function with given name.

        :param code: the source code to split.
        :param func_name: name of the function to create.
        :return: strings representing import_block, code_block, main_block.
        """
        # We split the lines in import and code blocks and join them to full code test
        lines = code.split("\n")
        ast_tree = ast.parse(code)
        # Imports are at the top, find where they end
        end_of_imports_line_num = 0
        for node in ast_tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            else:
                end_of_imports_line_num = node.lineno - 1
                break

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
            _import_block, _code_block, _ = self.split_code_blocks(
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
            self.db.get_session_context(self.session_id).working_directory
        )
        return repr(
            str(
                working_directory.relative_to(
                    (linea_folder() / "..").resolve()
                )
            )
        )
