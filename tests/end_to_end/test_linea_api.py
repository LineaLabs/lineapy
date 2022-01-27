def test_save_returns_artifact(execute):
    c = """import lineapy
x = 1
res = lineapy.save(x, "x")
slice = res.code
value = res.value
"""

    res = execute(c)
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
lineapy.save(x, "xold")

res = lineapy.get("xold")
y = res.value + 1
lineapy.save(y, "y")
"""

    res = execute(c)
    assert (
        res.artifacts["xold"]
        == """x = 1
"""
    )
    assert (
        res.artifacts["y"]
        == """import lineapy
res = lineapy.get("xold")
y = res.value + 1
"""
    )
    assert res.values["y"] == 2


def test_save_different_session(execute):
    execute("import lineapy\nlineapy.save(10, 'xx')")
    c = """import lineapy
y = lineapy.get('xx').value + 10
lineapy.save(y, 'y')
"""
    res = execute(c)
    assert res.values["y"] == 20
    assert (
        res.artifacts["y"]
        == """import lineapy
y = lineapy.get('xx').value + 10
"""
    )
