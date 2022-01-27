def test_list_setitem_mutates(execute):
    code = """x = []
x.append(10)
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code


def test_list_getitem_view(execute):
    code = """y = []
x = [y]
y.append(10)
"""
    res = execute(code, artifacts=["x"])
    assert res.slice("x") == code


# def test_list_append_mutates(execute):
#     code = """x = []
# x.append(10)
# """
#     res = execute(code, artifacts=["x"])
#     assert res.slice("x") == code


def test_list_append_mutates_inner(execute):
    code = """xinner = []
youter = [xinner]
xinner.append(10)
youter[0].append(11)
"""
    res = execute(code, artifacts=["xinner", "youter"])
    assert res.slice("xinner") == code
    assert res.slice("youter") == code
