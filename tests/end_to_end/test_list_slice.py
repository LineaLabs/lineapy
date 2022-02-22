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
