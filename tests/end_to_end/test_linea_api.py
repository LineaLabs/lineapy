def test_save_returns_artifact(execute):
    c = """import lineapy
x = 1
res = lineapy.save(x, "x")
slice = res.code
value = res.value
"""

    res = execute(c, test_re_execution=False)
    assert (
        res.artifacts["x"]
        == """x = 1
"""
    )
    assert res.values["slice"] == res.artifacts["x"]
    assert res.values["value"] == res.values["x"]


def test_get_returns_artifact(execute):
    c = """import lineapy
x = 1
lineapy.save(x, "x")

res = lineapy.get("x")
y = res.value + 1
lineapy.save(y, "y")
"""

    res = execute(c, test_re_execution=False)
    assert (
        res.artifacts["x"]
        == """x = 1
"""
    )
    assert (
        res.artifacts["y"]
        == """import lineapy
res = lineapy.get("x")
y = res.value + 1
"""
    )
    assert res.values["y"] == 2


def test_save_different_session(execute):
    execute("import lineapy\nlineapy.save(10, 'x')", test_re_execution=False)
    c = """import lineapy
y = lineapy.get('x').value + 10
lineapy.save(y, 'y')
"""
    res = execute(c, test_re_execution=False)
    assert res.values["y"] == 20
    assert (
        res.artifacts["y"]
        == """import lineapy
y = lineapy.get('x').value + 10
"""
    )
