import pytest


def test_pandas_subscript(execute):
    code = """import pandas as pd
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
df["C"] = df["A"] + df["B"]
"""
    res = execute(code, artifacts=["df"])
    # assert res.values["df"].to_csv(index=False) == "A,B,C\n1,4,5\n2,5,7\n3,6,9\n"
    assert res.artifacts["df"] == code
