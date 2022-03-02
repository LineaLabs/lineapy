import os
from pathlib import Path

import pytest

from lineapy.plugins.airflow import split_code_blocks

# @pytest.mark.parametrize(
#     "code, func_name, import_block, code_block, main_block",
#     [
#         (
#             """import numpy\na = 1""",
#             "abc",
#             "import numpy",
#             "def abc():\n\ta = 1",
#             'if __name__ == "__main__":\n\tprint(abc())',
#         ),
#         (
#             """from typing import (
#     Callable,
#     Dict,
#     Hashable,
#     Iterable,
#     List,
#     Optional,
#     Tuple,
#     Union,
# )
# a = 1
# """,
#             "abc",
#             """from typing import (
#     Callable,
#     Dict,
#     Hashable,
#     Iterable,
#     List,
#     Optional,
#     Tuple,
#     Union,
# )""",
#             "def abc():\n\ta = 1\n\t",
#             'if __name__ == "__main__":\n\tprint(abc())',
#         ),
#     ],
#     ids=[
#         "single_import",
#         "multi_line_import",
#     ],
# )


@pytest.mark.parametrize(
    "casename", ["single_import", "multi_line_import", "demo_1_preprocessing"]
)
def test_split_code_blocks(casename):
    test_folder = (
        Path(os.path.dirname(__file__)) / "split_test_cases" / casename
    )
    code = (test_folder / "code.txt").read_text()
    expected_import_block = (test_folder / "import_block.txt").read_text()
    expected_code_block = (test_folder / "code_block.txt").read_text()
    expected_main_block = (test_folder / "main_block.txt").read_text()
    _import_block, _code_block, _main_block = split_code_blocks(code, casename)
    assert _import_block == expected_import_block
    assert _code_block == expected_code_block
    assert _main_block == expected_main_block
