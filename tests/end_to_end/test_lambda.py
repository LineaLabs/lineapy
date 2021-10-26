def test_lambda_with_primitives(execute):
    code = """a = 10
b = lambda x: x + 10
c = b(a)
"""
    res = execute(code)
    assert res.values["c"] == 20


def test_lambda_with_external_vars(execute):
    code = """a = 10
b = lambda x: x + a
c = b(10)
"""
    res = execute(code)
    assert res.values["c"] == 20


def test_lambda_late_binding(execute):
    code = """a = 10
b = lambda: a
a = 11
c = b()"""
    res = execute(code)
    assert res.values["c"] == 11


def test_lambda_as_filter_w_primites(execute):
    code = """list_1 = [1,2,3,4,5,6,7,8,9]
list_2 = list(filter(lambda x: x%2==0, list_1))
"""
    res = execute(code)
    assert res.values["list_2"] == [2, 4, 6, 8]

    code2 = """list_1 = [1,2,3,4]
cubed = map(lambda x: pow(x,3), list_1)
final_value = list(cubed)"""

    res2 = execute(code2)
    assert res2.values["final_value"] == [1, 8, 27, 64]


def test_lambda_slicing_creates_correct_artifact_w_primitives(execute):
    code = """a = 10
b = lambda x: x + 10
c = b(a)
"""
    res = execute(code, artifacts=["c"])
    assert res.artifacts["c"] == code


def test_lambda_slicing_creates_correct_artifact_w_external_vars(execute):
    code = """a = 10
b = lambda x: x + a
c = b(10)
"""
    res = execute(code, artifacts=["c"])
    assert res.artifacts["c"] == code


# @pytest.mark.xfail
def test_knows_map_calls(execute):
    code = """a = 10
fn = lambda x: a + x
r = sum(map(fn, [1]))
"""
    res = execute(code, artifacts=["r"])
    assert res.values["r"] == 11
    assert res.artifacts["r"] == code


# @pytest.mark.xfail
def test_knows_call_list(execute):
    code = """a = 10
fn = lambda: a
def sum_call_list(xs):
    r = 0
    for x in xs:
        r += x()
    return r
r = sum_call_list([fn, fn])
"""
    res = execute(code, artifacts=["r"])
    assert res.values["r"] == 20
    assert res.artifacts["r"] == code
