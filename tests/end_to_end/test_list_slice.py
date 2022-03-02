def test_empty_slice(execute):
    res = execute("x = [1, 2, 3][:]", snapshot=False)
    assert res.values["x"] == [1, 2, 3]


def test_slice_with_step(execute):
    res = execute("x = [1, 2, 3][::2]", snapshot=False)
    assert res.values["x"] == [1, 3]


def test_slice_with_step_and_start(execute):
    res = execute("x = [1, 2, 3][0::2]", snapshot=False)
    assert res.values["x"] == [1, 3]


def test_slice_with_step_and_stop(execute):
    res = execute("x = [1, 2, 3][:2:2]", snapshot=False)
    assert res.values["x"] == [1]


def test_slice_with_step_and_start_and_stop(execute):
    res = execute("x = [1, 2, 3][1:2:2]", snapshot=False)
    assert res.values["x"] == [2]


def test_slice_with_start(execute):
    res = execute("x = [1, 2, 3][1:]", snapshot=False)
    assert res.values["x"] == [2, 3]


def test_subscript(execute):
    SUBSCRIPT = """
ls = [1,2,3,4]
ls[0] = 1
a = 4
ls[1] = a
ls[2:3] = [30]
ls[3:a] = [40]
"""
    res = execute(SUBSCRIPT, snapshot=False)
    assert len(res.values["ls"]) == 4
    assert res.values["ls"][0] == 1
    assert res.values["ls"][1] == 4
    assert res.values["ls"][2] == 30
    assert res.values["ls"][3] == 40
