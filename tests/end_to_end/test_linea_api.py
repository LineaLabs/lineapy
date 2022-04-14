def test_save_returns_artifact(execute):
    c = """import lineapy
x = 1
res = lineapy.save(x, "x")
slice = res.get_code()
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
lineapy.save(x, "x")

res = lineapy.get("x")
y = res.value + 1
lineapy.save(y, "y")
"""

    res = execute(c)
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
    execute("import lineapy\nlineapy.save(10, 'x')")
    c = """import lineapy
y = lineapy.get('x').value + 10
lineapy.save(y, 'y')
"""
    res = execute(c)
    assert res.values["y"] == 20
    assert (
        res.artifacts["y"]
        == """import lineapy
y = lineapy.get('x').value + 10
"""
    )


def test_save_twice(execute):
    res = execute(
        """import lineapy
x = 100
lineapy.save(x, 'x')
lineapy.save(x, 'x')
y = 100
lineapy.save(y, 'y')
"""
    )
    assert res.values["x"] == 100
    assert res.artifacts["x"] == "x = 100\n"
    assert res.values["y"] == 100
    assert res.artifacts["y"] == "y = 100\n"
