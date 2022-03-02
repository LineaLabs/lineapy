def test_alias(execute):
    code = """import lineapy
x = 100
y = x
lineapy.save(y, "y")
"""
    res = execute(code, snapshot=False)
    assert res.slice("y") == "x = 100\ny = x\n"
