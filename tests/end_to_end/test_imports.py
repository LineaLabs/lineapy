# import x
def test_basic_import(execute):
    code = """import math
x = math.sqrt(64)
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 8
    assert res.artifacts["x"] == code


# import x as a
def test_basic_import_as(execute):
    code = """import math as m
x = m.sqrt(64)
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 8
    assert res.artifacts["x"] == code


# # import x.y.z
# def test_nested_import(execute):
#     code = """import matplotlib.pyplot
# x = matplotlib.pyplot
# """
#     res = execute(code, artifacts=["x"])
#     assert res.artifacts["x"] == code


# # import x.y.z as a
# def test_nested_import_as(execute):
#     code = """import matplotlib.pyplot as plt
# """
#     res = execute(code, artifacts=["x"])
#     assert res.artifacts["x"] == code


# from x import y
def test_basic_from_import(execute):
    code = """from math import sqrt
x = sqrt(64)
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 8
    assert res.artifacts["x"] == code


# from x import *
# from x import y as a
# from x.y import z
# from x.y import *
# from x.y import z as a
