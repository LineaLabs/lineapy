import pytest


def test_PIL_import_fs_artifact(execute):
    code = """from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")
"""
    res = execute(code, artifacts=["e"])
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


def test_pandas_to_sql_global_imported(execute):
    code = """from lineapy import save, db
import pandas as pd
import sqlite3

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
conn = sqlite3.connect(':memory:')
df.to_sql(name="test", con=conn,index=False)

save(db, "db")
"""
    res = execute(code)
    assert (
        res.artifacts["db"]
        == """from lineapy import save, db
import pandas as pd
import sqlite3
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
conn = sqlite3.connect(':memory:')
df.to_sql(name="test", con=conn,index=False)
"""
    )


def test_pandas_to_csv(execute):
    code = """import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_csv("test.csv", index=False)
df2 = pd.read_csv("test.csv")
"""
    res = execute(code, artifacts=["df2"])
    assert res.values["df2"].to_csv(index=False) == "a,b\n1,4\n2,5\n3,6\n"
    assert res.artifacts["df2"] == code


def test_pandas_to_parquet(execute):
    code = """import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_parquet("test.parquet", index=False)
df2 = pd.read_parquet("test.parquet")
"""
    res = execute(code, artifacts=["df2"])
    assert res.values["df2"].to_csv(index=False) == "a,b\n1,4\n2,5\n3,6\n"
    assert res.artifacts["df2"] == code


@pytest.mark.xfail(reason="Path based dependencies not working")
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


mincode = """import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
"""

extras = """import sqlite3
conn = sqlite3.connect(':memory:')
"""

to_sql = 'df.to_sql(name="test", con=conn,index=False)'
to_parquet = 'df.to_parquet("df.parquet")'


def test_to_sql_does_not_slice(execute):
    res = execute(mincode + extras + to_sql, artifacts=["df"])
    assert res.artifacts["df"] == mincode


##
# File system and DB side effects
##


def test_slicing_db(execute):
    code = mincode + extras + to_sql + "\n"
    res = execute(code, artifacts=["lineapy.db"])
    assert res.artifacts["lineapy.db"] == code


def test_slicing_filesystem(execute):
    code = mincode + extras + to_parquet
    res = execute(code, artifacts=["lineapy.file_system"])
    assert res.artifacts["lineapy.file_system"] == mincode + to_parquet + "\n"
