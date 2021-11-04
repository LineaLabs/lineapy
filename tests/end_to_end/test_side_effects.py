import pytest


def test_PIL_import_fs_artifact(execute):
    code = """from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")
"""
    res = execute(code, artifacts=["e"])
    print(res.artifacts["e"])
    assert res.artifacts["e"] == code


def test_pandas_to_sql(execute):
    code = """import pandas as pd
import sqlite3
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
conn = sqlite3.connect(':memory:')
df.to_sql(name="test", con=conn,index=False)
df2 = pd.read_sql("select * from test", conn)
"""
    res = execute(code, artifacts=["df2"])
    assert res.values["df2"].to_csv(index=False) == "a,b\n1,4\n2,5\n3,6\n"
    assert res.artifacts["df2"] == code


def test_pandas_to_csv(execute):
    code = """import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_csv("test.csv", index=False)
df2 = pd.read_csv("test.csv")
"""
    res = execute(code, artifacts=["df2"])
    assert res.values["df2"].to_csv(index=False) == "a,b\n1,4\n2,5\n3,6\n"
    assert res.artifacts["df2"] == code


@pytest.mark.xfail(reason="ideally we want to get to this point")
def test_needless_vars_do_not_get_included(execute):
    code = """import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_csv("test.csv", index=False)
df2 = pd.read_csv("test.csv")
df2["c"] = df2["a"] + df2["b"]
df2.to_csv("test2.csv", index=False)
df3 = pd.read_csv("test.csv")
"""
    expectedcode = """import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_csv("test.csv", index=False)
df3 = pd.read_csv("test.csv")
"""
    res = execute(code, artifacts=["df3"])
    assert res.values["df3"].to_csv(index=False) == "a,b\n1,4\n2,5\n3,6\n"
    assert res.artifacts["df3"] == expectedcode
