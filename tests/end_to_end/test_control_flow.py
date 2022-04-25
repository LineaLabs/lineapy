def test_loop_code(execute):
    LOOP_CODE = """a = []
b = 0
for x in range(9):
    a.append(x)
    b += x
x = sum(a)
y = x + b
"""
    res = execute(LOOP_CODE, artifacts=["y"])

    assert len(res.values["a"]) == 9
    assert res.values["x"] == 36
    assert res.values["b"] == 36
    assert res.values["y"] == 72
    assert res.slice("y") == LOOP_CODE


def test_conditionals(execute):
    CONDITIONALS_CODE = """bs = [1,2]
if len(bs) > 4:
    pass
else:
    bs.append(3)
"""
    res = execute(CONDITIONALS_CODE)
    assert res.values["bs"] == [1, 2, 3]


def test_while_executes_and_scopes_correctly(execute):
    SAMPLE_WHILE = """x = [1, 2, 3]
idx = 0
result = 0
while idx < len(x):
    result += x[idx]
    idx += 1
"""
    res = execute(SAMPLE_WHILE, artifacts=["result"])
    assert res.values["result"] == 6
    assert res.artifacts["result"] == SAMPLE_WHILE
