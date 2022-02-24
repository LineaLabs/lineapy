LINEA_IMPORT_CODE = """import lineapy
"""
LOOP_CODE_BODY = """a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
"""
LINEA_ARTIFACT_CODE = "lineapy.save(y, 'y')"

LOOP_CODE = LINEA_IMPORT_CODE + LOOP_CODE_BODY + LINEA_ARTIFACT_CODE


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

    assert res.slice("y") == LOOP_CODE_BODY
