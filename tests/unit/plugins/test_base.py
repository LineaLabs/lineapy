import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from lineapy.plugins.base import BasePlugin  # split_code_blocks


@pytest.mark.parametrize(
    "casename",
    [
        "single_import",
        "multi_line_import",
        "demo_1_preprocessing",
        "heartbeat",
    ],
)
def test_split_code_blocks(casename):
    bp = BasePlugin(MagicMock(), MagicMock())
    test_folder = (
        Path(os.path.dirname(__file__)) / "split_test_cases" / casename
    )
    code = (test_folder / "code.txt").read_text()
    expected_import_block = (test_folder / "import_block.txt").read_text()
    expected_code_block = (test_folder / "code_block.txt").read_text()
    expected_main_block = (test_folder / "main_block.txt").read_text()
    _import_block, _code_block, _main_block = bp.split_code_blocks(
        code, casename
    )
    assert _import_block == expected_import_block
    assert _code_block == expected_code_block
    assert _main_block == expected_main_block
