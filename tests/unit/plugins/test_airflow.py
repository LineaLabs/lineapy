import pytest

from lineapy.plugins.airflow import split_code_blocks


@pytest.mark.parametrize(
    "code, func_name, import_block, code_block, main_block",
    [
        (
            """import numpy\na = 1""",
            "abc",
            "import numpy",
            "def abc():\n\ta = 1",
            'if __name__ == "__main__":\n\tprint(abc())',
        ),
        (
            """from typing import (
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)
a = 1
""",
            "abc",
            """from typing import (
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)""",
            "def abc():\n\ta = 1\n\t",
            'if __name__ == "__main__":\n\tprint(abc())',
        ),
    ],
    ids=[
        "single_import",
        "multi_line_import",
    ],
)
def test_split_code_blocks(
    code, func_name, import_block, code_block, main_block
):
    _import_block, _code_block, _main_block = split_code_blocks(
        code, func_name
    )
    assert _import_block == import_block
    assert _code_block == code_block
    assert _main_block == main_block
