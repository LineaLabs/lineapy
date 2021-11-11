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
