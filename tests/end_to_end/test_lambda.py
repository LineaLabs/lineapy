import os

import pytest


@pytest.mark.parametrize(
    "filename, asserttype, asserts",
    [("data/lambda_01.py", "value", [("c", 20)])],
)
def test_import(execute, filename, asserttype, asserts):
    # starting python 3.9, __file__ gives full path yaay
    with open(f"{os.path.dirname(__file__)}/{filename}", "r") as f:
        code = f.read()
        res = execute(code)
        if asserttype == "value":
            for (var, value) in asserts:
                assert res.values[var] == value
