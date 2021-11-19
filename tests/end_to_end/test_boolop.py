import pytest

SAMPLE_BOOLOP = """print(True and False)
print(True or False)
x = True and False
"""

S_BOOLOP2 = """x = 1>2
y = 1<2
#z = x and y
q = (1>2 or 1<2)
"""


@pytest.mark.xfail
def test_boolop_execute(execute):
    res = execute(SAMPLE_BOOLOP)
    assert res.values["x"] is False


@pytest.mark.xfail
def test_boolop2_execute(execute):
    res = execute(S_BOOLOP2)
    assert res.values["q"] is False
