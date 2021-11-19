SAMPLE_WHILE = """x=[1,2,3]
idx=0
result = 0
while idx<len(x):
    result += x[idx]
    idx += 1
"""


def test_while_doest_puke(execute):
    res = execute(SAMPLE_WHILE)
    assert res.values["result"] == 6


def test_while_scopes_correctly(execute):
    res = execute(SAMPLE_WHILE, artifacts=["result"])
    assert res.artifacts["result"] == SAMPLE_WHILE
