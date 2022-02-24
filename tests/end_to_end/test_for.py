LOOP_CODE = """import lineapy
a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
lineapy.save(y, 'y')
"""


def test_loop_code(execute):
    res = execute(LOOP_CODE)

    assert len(res.values["a"]) == 9
    assert res.values["x"] == 36
    assert res.values["b"] == 36
    assert res.values["y"] == 72


def test_loop_code_slice(execute, python_snapshot):
    res = execute(
        LOOP_CODE,
        snapshot=False,
    )

    assert res.slice("y") == python_snapshot
