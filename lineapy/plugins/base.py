import ast
import fnmatch
import logging
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import tempdir
from typing import Dict, Optional

import isort

from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.plugins.utils import get_lib_version_text, load_plugin_template
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import prettify

logger = logging.getLogger(__name__)
configure_logging()


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

    def prepare_output_dir(self, copy_src: str, copy_dst: str):
        """
        This helper creates directories if missing and copies over non-python files from the source directory.
        This is done to copy any config/data files to the output directory.
        """

        if copy_src == copy_dst:
            # special case that we can allow. skip everything if source and destination
            # are the same (typically when output is dumped in the current working dir
            # eg. during tests)
            return

        # ignores = shutil.ignore_patterns(
        #     "*.py",
        #     "*.ipynb",
        #     "*.ipynb_checkpoints",
        #     "*.pyc",
        #     "*.pyo",
        #     "*.egg-info",
        #     "*.toml",
        #     "__*__",
        #     ".*",
        # )

        def include_patterns(patterns, blacklist_dir=None):
            """
            Based on shutil.ignore_patterns, this is a similar function
            to include certain patterns instead. It gives the complementary set of
            shutil.ignore_patterns.
            original docstring:
            Function that can be used as copytree() exclude parameter.

            Patterns is a sequence of glob-style patterns
            that are used to exclude files

            """

            def _ignore_patterns(path, names):
                ignored_names = []
                for pattern in patterns:
                    ignored_names.extend(fnmatch.filter(names, pattern))
                dirnames = {
                    dname
                    for dname in os.listdir(path)
                    if os.path.isdir(os.path.join(path, dname))
                }
                if not blacklist_dir or len(blacklist_dir) == 0:
                    ignored_names.extend(dirnames)
                else:
                    for blacklistpattern in blacklist_dir:
                        ignored_names.extend(
                            dirnames
                            - set(fnmatch.filter(dirnames, blacklistpattern))
                        )

                return set(names) - set(ignored_names)

            return _ignore_patterns

        includes = include_patterns(
            patterns=["*.csv", "*.cfg", "*.yaml"],
            blacklist_dir=["__*__"],
        )
        # getting dir exists error for py 3.7 here. no way to reliably do it so doing it in a dev-friendly way.
        # purging out the destination folder for now. If this becomes an issue, someone can file it and
        # we can handle the delete more intelligently. For now just making sure that clearing out destination
        # does not clear out our source folder
        if not Path(copy_dst) in Path(copy_src).parents and os.path.exists(
            copy_dst
        ):
            shutil.rmtree(copy_dst)

        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copytree(copy_src, temp_dir, ignore=includes, dirs_exist_ok=True)
            self.removeEmptyFolders(temp_dir)
            shutil.copytree(temp_dir, copy_dst)

    def removeEmptyFolders(self, path, removeRoot=False):
        # Function to remove empty folders
        if not os.path.isdir(path):
            return

        # remove empty subfolders
        files = os.listdir(path)
        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    self.removeEmptyFolders(fullpath)

        # if folder empty, delete it
        files = os.listdir(path)
        if len(files) == 0 and removeRoot:
            os.rmdir(path)

    def generate_python_module(
        self,
        module_name: str,
        artifacts_code: Dict[str, str],
        output_dir_path: Path,
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
        output_dir: Optional[str] = None,
    ):
        """
        Generates templates to test the airflow module. Currently, we
        produce a <module_name>_Dockerfile and a <module_name>_requirements.txt file.
        These can be used to test the dag that gets generated by linea. For more
        details, :ref:`Testing locally <testingairflow>`
        """
        DOCKERFILE_TEMPLATE = load_plugin_template("dockerfile.jinja")
        dockerfile = DOCKERFILE_TEMPLATE.render(module_name=module_name)
        output_dir_path = Path(output_dir) if output_dir else Path.cwd()
        (output_dir_path / (module_name + "_Dockerfile")).write_text(
            dockerfile
        )
        logger.info(f"Generated Dockerfile {module_name}_Dockerfile")
        all_libs = self.db.get_libraries_for_session(self.session_id)
        lib_names_text = ""
        for lib in all_libs:
            if lib.name in sys.modules:
                text = get_lib_version_text(lib.name)
                lib_names_text += f"{text}\n"
        # lib_names_text = "\n".join([str(lib.name) for lib in all_libs])
        (output_dir_path / (module_name + "_requirements.txt")).write_text(
            lib_names_text
        )
        logger.info(
            f"Generated requirements file {module_name}_requirements.txt"
        )
