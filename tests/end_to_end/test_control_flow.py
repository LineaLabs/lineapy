import pytest


def test_loop_code(execute):
    LOOP_CODE = """a = []
b = 0
for x in range(9):
    a.append(x)
    b += x
x = sum(a)
y = x + b
"""
    res = execute(LOOP_CODE, artifacts=["y"])

    assert len(res.values["a"]) == 9
    assert res.values["x"] == 36
    assert res.values["b"] == 36
    assert res.values["y"] == 72
    assert res.slice("y") == LOOP_CODE


def test_conditionals(execute):
    CONDITIONALS_CODE = """bs = [1,2]
if len(bs) > 4:
    pass
else:
    bs.append(3)
"""
    res = execute(CONDITIONALS_CODE)
    assert res.values["bs"] == [1, 2, 3]


def test_while_executes_and_scopes_correctly(execute):
    SAMPLE_WHILE = """x = [1, 2, 3]
idx = 0
result = 0
while idx < len(x):
    result += x[idx]
    idx += 1
"""
    res = execute(SAMPLE_WHILE, artifacts=["result"])
    assert res.values["result"] == 6
    assert res.artifacts["result"] == SAMPLE_WHILE


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_should_slice_within_if(execute):
    # TODO: We only slice within a block if we can execute it. Later, we need
    # to be able to ensure we can perform slicing among unvisited blocks as
    # well
    CODE = """a = 10
b = 20
if a > 5:
    a = 5
    b = 6
"""
    res = execute(CODE, artifacts=["a", "b"])
    assert res.values["a"] == 5
    assert res.values["b"] == 6
    assert (
        res.artifacts["a"]
        == """a = 10
if a > 5:
    a = 5
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
@pytest.mark.xfail(
    reason="Variable overwritten in visited branch results in declaration outside slice being removed"
)
def test_if_should_not_slice_out_existing_variable_definitions_outside_block(
    execute,
):
    CODE = """a = 10
b = 20
if a > 5:
    a = 5
    b = 6
"""
    res = execute(CODE, artifacts=["a", "b"])
    assert res.values["a"] == 5
    assert res.values["b"] == 6
    assert (
        res.artifacts["b"]
        == """a = 10
b = 20
if a > 5:
    b = 6
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_should_slice_within_else(execute):
    # TODO: We only slice within a block if we can execute it. Later, we need
    # to be able to ensure we can perform slicing among unvisited blocks as
    # well
    CODE = """a = 10
b = 20
if a <= 5:
    a = 5
    b = 5
else:
    a = 100
    b = 101
"""
    res = execute(CODE, artifacts=["a", "b"])
    assert res.values["a"] == 100
    assert res.values["b"] == 101
    assert (
        res.artifacts["a"]
        == """a = 10
if a <= 5:
    a = 5
    b = 5
else:
    a = 100
"""
    )
    assert (
        res.artifacts["b"]
        == """a = 10
if a <= 5:
    a = 5
    b = 5
else:
    b = 101
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_should_not_slice_whole_block_out_if_unexecuted_block_present(
    execute,
):
    CODE = """a = 10
b = 20
if a >= 10:
    a += 1
else:
    a -= 1
"""
    res = execute(CODE, artifacts=["b"])
    assert (
        res.artifacts["b"]
        == """a = 10
b = 20
if a >= 10:
    pass
else:
    a -= 1
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_nested_should_slice_within_inner_if(execute):
    CODE = """a = 10
b = 20
if a > 0:
    if a > 2:
        a = 1
        b = 2
    else:
        a = 3
        b = 4
else:
    a = 5
    b = 6
"""
    res = execute(CODE, artifacts=["a"])
    assert res.values["a"] == 1
    assert res.values["b"] == 2
    assert (
        res.artifacts["a"]
        == """a = 10
if a > 0:
    if a > 2:
        a = 1
    else:
        a = 3
        b = 4
else:
    a = 5
    b = 6
"""
    )

    # TODO: Note that the sliced code would not run in case we visit a
    # different branch other than the one seen during the creation of the graph.
    # When static analysis is introduced, this test should be fixed.


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_nested_should_slice_within_inner_else(execute):
    CODE = """a = 10
b = 20
if a > 0:
    if a <= 2:
        a = 1
        b = 2
    else:
        a = 3
        b = 4
else:
    a = 5
    b = 6
"""
    res = execute(CODE, artifacts=["a"])
    assert res.values["a"] == 3
    assert res.values["b"] == 4
    assert (
        res.artifacts["a"]
        == """a = 10
if a > 0:
    if a <= 2:
        a = 1
        b = 2
    else:
        a = 3
else:
    a = 5
    b = 6
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_nested_should_slice_within_elif(execute):
    CODE = """a = 10
b = 20
if a <= 2:
    a = 1
    b = 2
elif a > 0:
    a = 3
    b = 4
else:
    a = 5
    b = 6
"""
    res = execute(CODE, artifacts=["a"])
    assert res.values["a"] == 3
    assert res.values["b"] == 4
    assert (
        res.artifacts["a"]
        == """a = 10
if a <= 2:
    a = 1
    b = 2
elif a > 0:
    a = 3
else:
    a = 5
    b = 6
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_all_lines_sliced_out_within_if(execute):
    CODE = """a = 10
if a < 20:
    b = 10
else:
    a += 20
"""
    res = execute(CODE, artifacts=["a"])
    assert (
        res.artifacts["a"]
        == """a = 10
if a < 20:
    pass
else:
    a += 20
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_all_lines_sliced_out_within_else(execute):
    CODE = """a = 10
if a >= 20:
    a += 20
else:
    b = 10
"""
    res = execute(CODE, artifacts=["a"])
    assert (
        res.artifacts["a"]
        == """a = 10
if a >= 20:
    a += 20
else:
    pass
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_slice_out_whole_block_if_no_unexecuted_branch(execute):
    CODE = """a = 10
if a < 20:
    b = 20
"""
    res = execute(CODE, artifacts=["a"])
    assert (
        res.artifacts["a"]
        == """a = 10
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
def test_if_do_not_slice_out_whole_block_if_no_unexecuted_branch_but_side_effects_in_conditions(
    execute,
):
    CODE = """a = [10]
if a.pop():
    b = 20
"""
    res = execute(CODE, artifacts=["a"])
    assert (
        res.artifacts["a"]
        == """a = [10]
if a.pop():
    pass
"""
    )


@pytest.mark.skip(reason="Unhide after LIN-532")
@pytest.mark.skipif("sys.version_info < (3, 8)")
def test_if_side_effect_in_condition(execute):
    CODE = """a = [1, 2, 3]
if b := a.pop():
    b += 1
"""
    res = execute(CODE, snapshot=False, artifacts=["a"])
    assert (
        res.artifacts["a"]
        == """a = [1, 2, 3]
if b := a.pop():
    pass
"""
    )
    # assert res.artifacts["b"] == CODE
