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


def test_if_should_slice_within_if(execute):
    # TODO: We only slice within a block if we can execute it. Later, we need to be able to ensure we can perform slicing among unvisited blocks as well
    CODE = """a = 10
b = 20
if a > 5:
    a = 5
    b = 6
"""
    res = execute(CODE, artifacts=["a", "b"])
    assert res.values["a"] == 5
    assert res.values["b"] == 6
    assert "b = 6" not in res.artifacts["a"]
    assert "a = 5" not in res.artifacts["b"]


def test_if_should_slice_within_else(execute):
    # TODO: We only slice within a block if we can execute it. Later, we need to be able to ensure we can perform slicing among unvisited blocks as well
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
    assert "b = 101" not in res.artifacts["a"]
    assert "a = 100" not in res.artifacts["b"]


def test_if_should_slice_whole_block_out(execute):
    CODE = """a = 10
b = 20
if b >= 10:
    a += 1
else:
    a -= 1
"""
    res = execute(CODE, artifacts=["b"])
    assert res.artifacts["b"] == "b = 20\n"


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
    assert "b = 2" not in res.artifacts["a"]


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
    assert "b = 4" not in res.artifacts["a"]
