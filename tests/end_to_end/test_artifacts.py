def test_set_one_artifact(execute):
    code = """import lineapy
x = []
lineapy.save(x, "x")
"""
    res = execute(code, snapshot=False)
    assert res.slice("x") == "x = []\n"


def test_overwrite_artifact(execute):
    code = """import lineapy
x = []
lineapy.save(x, "x")
x = 10
lineapy.save(x, "x")
"""
    res = execute(code, snapshot=False)
    assert res.slice("x") == "x = 10\n"


def test_alias_artifact(execute):
    code = """import lineapy
x = []
lineapy.save(x, "x")
lineapy.save(x, "x2")
"""
    res = execute(code, snapshot=False)
    assert res.slice("x") == "x = []\n"
    assert res.slice("x2") == "x = []\n"


def test_bad_artifact_save_fails_and_recovers(execute):
    code = """import pandas
import lineapy
x=1
y=1
lineapy.save(y,"workstoo")
lineapy.save(pandas,"fails")
lineapy.save(x,"works")
"""
    res = execute(code, snapshot=False)
    assert res.values["x"] == 1
