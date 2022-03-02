def test_basic_dict(execute):
    res = execute("x = {'a': 1, 'b': 2}")
    assert res.values["x"] == {"a": 1, "b": 2}


def test_splatting(execute):
    res = execute("x = {1: 2, 2:2, **{1: 3, 2: 3}, 1: 4}")
    assert res.values["x"] == {1: 4, 2: 3}


def test_dictionary_support(execute):
    DICTIONARY_SUPPORT = """import pandas as pd
df = pd.DataFrame({"id": [1,2]})
x = df["id"].sum()
"""
    res = execute(DICTIONARY_SUPPORT)
    assert res.values["x"] == 3
