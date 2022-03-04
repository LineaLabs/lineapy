def test_returns_value(execute):
    res = execute("x = [i + 1 for i in range(3)]")
    assert res.values["x"] == [1, 2, 3]


def test_depends_on_prev_value(execute):
    res = execute(
        "y = range(3)\nx = [i + 1 for i in y]",
        snapshot=False,
        artifacts=["x"],
    )
    # Verify that i isn't set in the local scope
    assert res.values["x"] == [1, 2, 3]
    assert res.values["y"] == range(3)
    assert "i" not in res.values
    sliced_code = res.slice("x")
    assert execute(sliced_code).values["x"] == [1, 2, 3]
