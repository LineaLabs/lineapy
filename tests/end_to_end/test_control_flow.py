LINEA_IMPORT_CODE = """import lineapy
"""
FOR_LOOP_CODE_BODY = """a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
"""
LINEA_ARTIFACT_CODE = "lineapy.save(y, 'y')"

LOOP_CODE = LINEA_IMPORT_CODE + FOR_LOOP_CODE_BODY + LINEA_ARTIFACT_CODE


def test_loop_code(execute):
    res = execute(LOOP_CODE)

    assert len(res.values["a"]) == 9
    assert res.values["x"] == 36
    assert res.values["b"] == 36
    assert res.values["y"] == 72


def test_loop_code_slice(execute):
    res = execute(
        LOOP_CODE,
        snapshot=False,
    )

    assert res.slice("y") == FOR_LOOP_CODE_BODY


CONDITIONALS_CODE = """bs = [1,2]
if len(bs) > 4:
    pass
else:
    bs.append(3)
"""


def test_conditionals(execute):
    res = execute(CONDITIONALS_CODE)
    assert res.values["bs"] == [1, 2, 3]


SAMPLE_WHILE = """x=[1,2,3]
idx=0
result = 0
while idx<len(x):
    result += x[idx]
    idx += 1
"""


def test_while_executes_correctly(execute):
    res = execute(SAMPLE_WHILE)
    assert res.values["result"] == 6


def test_while_scopes_correctly(execute):
    res = execute(SAMPLE_WHILE, artifacts=["result"])
    assert res.artifacts["result"] == SAMPLE_WHILE
