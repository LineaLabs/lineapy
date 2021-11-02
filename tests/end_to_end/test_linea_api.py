def test_save_get_same_session(execute):
    c = """x = 1
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
        == """x = 1
lineapy.save(x, "x")
res = lineapy.get("x")
y = res.value + 1
"""
    )


def test_slice(execute):
    c = """x = 1
print(lineapy.save(x).slice)"""

    res = execute(c)
    assert (
        res.stdout
        == """x = 1
"""
    )


def test_save_different_session(execute):
    execute("lineapy.save(10, 'x')")
    c = """y = lineapy.get('x').value
lineapy.save(y + 10, 'y')
"""
    res = execute(c)
    assert res.values["y"] == 20
    assert res.artifacts["y"] == c
