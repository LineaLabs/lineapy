CONDITIONALS_CODE = """bs = [1,2]
if len(bs) > 4:
    pass
else:
    bs.append(3)
"""


def test_conditionals(execute):
    res = execute(CONDITIONALS_CODE)
    assert res.values["bs"] == [1, 2, 3]
