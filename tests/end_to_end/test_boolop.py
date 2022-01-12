SAMPLE_BOOLOP = """print(True and False)
print(True or False)
x = True and False
"""

S_BOOLOP2 = """x = 1>2
y = 1<2
z = x and y
q = (1>2 or 1<2)
"""


def test_boolop_execute(execute):
    res = execute(SAMPLE_BOOLOP)
    assert res.values["x"] is False


def test_boolop2_execute(execute):
    res = execute(S_BOOLOP2)
    assert res.values["q"] is True
    assert res.values["z"] is False
