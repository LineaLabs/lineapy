def test_import_multiple_with_alias(execute):
    code = """from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
"""
    res = execute(code)
    assert res.values["a"] == 25
    assert res.values["b"] == 5


def test_PIL_import_issue(execute):
    code = """from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")"""
    res = execute(code)
    assert res.values["e"].__class__.__name__ == "PngImageFile"


def test_import_multiple_without_alias(execute):
    code = """import pandas, numpy
c = pandas.DataFrame()
d = numpy.array([1,2,3])
"""
    res = execute(code)
    assert res.values["c"].__class__.__name__ == "DataFrame"
    assert (res.values["d"] == [1, 2, 3]).all()


def test_repeat_imports(execute):
    code = """from math import pow
from math import sqrt
a=pow(5,2)
b=sqrt(a)
"""
    res = execute(code, artifacts=["a", "b"])
    assert res.values["a"] == 25
    assert res.values["b"] == 5
    assert res.artifacts["b"] == code
    assert (
        res.artifacts["a"]
        == """from math import pow
a=pow(5,2)
"""
    )
