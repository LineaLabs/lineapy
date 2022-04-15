import pytest

from lineapy.utils.utils import prettify


def test_import_multiple_with_alias(execute):
    code = """from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
"""
    res = execute(code)
    assert res.values["a"] == 25
    assert res.values["b"] == 5


@pytest.mark.slow
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
    assert res.artifacts["b"] == prettify(code)
    assert res.artifacts["a"] == prettify(
        """from math import pow
a=pow(5,2)
"""
    )


def test_import_mutable(execute):
    code = """import pandas
pandas.x = 1
y = pandas.x
"""
    res = execute(code, artifacts=["y"])
    assert res.values["y"] == 1
    assert res.artifacts["y"] == prettify(code)


def test_import_with_alias(execute):
    code = """import pandas as pd
y = pd.DataFrame()
"""
    res = execute(code, artifacts=["y"])
    assert res.values["y"].__class__.__name__ == "DataFrame"
    assert res.artifacts["y"] == prettify(code)


@pytest.mark.xfail(reason="https://github.com/LineaLabs/lineapy/issues/383")
def test_imports_linked(execute):
    code = """import pandas
import pandas as pd
pandas.x = 1
y = pd.x
"""
    res = execute(code, artifacts=["y"])
    assert res.values["y"] == 1
    assert res.artifacts["y"] == prettify(code)


def test_import_star(execute):
    code = """from math import *
mypi = pi
x = sqrt(4)
"""
    res = execute(code, snapshot=False)
    assert res.values["mypi"] == 3.141592653589793
    assert res.values["x"] == 2.0


@pytest.mark.xfail(reason="import submodule")
class TestSubmodule:
    def test_from(self, execute):
        """
        Test import a submodule from a parent
        """

        code = """from lineapy.utils import __no_imported_submodule
is_prime = __no_imported_submodule.is_prime
"""
        res = execute(code, artifacts=["is_prime"])
        assert res.values["is_prime"] is False
        assert res.artifacts["is_prime"] == prettify(code)

    def test_direct(self, execute):
        """
        Test importing a submodule and referring to it directly
        """

        code = """import lineapy.utils.__no_imported_submodule
is_prime = lineapy.utils.__no_imported_submodule.is_prime
"""
        res = execute(code, artifacts=["is_prime"])
        assert res.values["is_prime"] is False
        assert res.artifacts["is_prime"] == prettify(code)

    def test_error_not_imported(self, execute):
        """
        Verify that trying to access a not imported submodule raises an AttributeError
        """

        code = """import lineapy.utils
is_prime = lineapy.utils.__no_imported_submodule.is_prime
"""
        with pytest.raises(AttributeError):
            execute(code, snapshot=False)

    def test_slice_parent(self, execute):
        """
        Test that slicing on a submodule should remove the import for the parent
        """

        code = """import lineapy.utils.__no_imported_submodule
import lineapy.utils
is_prime = lineapy.utils.__no_imported_submodule.is_prime
"""
        res = execute(code, artifacts=["is_prime"])
        assert res.values["is_prime"] is False
        assert (
            res.artifacts["is_prime"]
            == """import lineapy.utils.__no_imported_submodule
is_prime = lineapy.utils.__no_imported_submodule.is_prime
"""
        )

    def test_slice_sibling(self, execute):
        """
        Test importing a submodule and referring to it directly, should have a different slice
        """

        code = """import lineapy.utils.__no_imported_submodule
import lineapy.utils.__no_imported_submodule_prime
first_is_prime = lineapy.utils.__no_imported_submodule.is_prime
second_is_prime = lineapy.utils.__no_imported_submodule_prime.is_prime
"""
        res = execute(code, artifacts=["first_is_prime", "second_is_prime"])
        assert res.values["first_is_prime"] is False
        assert res.values["second_is_prime"] is True
        assert (
            res.artifacts["first_is_prime"]
            == """import lineapy.utils.__no_imported_submodule
first_is_prime = lineapy.utils.__no_imported_submodule.is_prime
"""
        )
        assert (
            res.artifacts["second_is_prime"]
            == """import lineapy.utils.__no_imported_submodule_prime
second_is_prime = lineapy.utils.__no_imported_submodule_prime.is_prime
"""
        )


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


# from x import y
def test_basic_from_import(execute):
    code = """from math import sqrt
x = sqrt(64)
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 8
    assert res.artifacts["x"] == code


# from x import y as a
def test_basic_from_import_as(execute):
    code = """from math import sqrt as sq
x = sq(64)
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 8
    assert res.artifacts["x"] == code


# from x import *
def test_basic_from_import_starred(execute):
    code = """from math import *
x = sqrt(64)
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"] == 8
    assert res.artifacts["x"] == code


# import x.y.z
def test_nested_import(execute):
    code = """import matplotlib.pyplot
x = matplotlib.pyplot.ylabel('label')
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"].__class__.__name__ == "Text"
    assert res.artifacts["x"] == code


# import x.y.z as a
def test_nested_import_as(execute):
    code = """import matplotlib.pyplot as plt
x = plt.ylabel('label')
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"].__class__.__name__ == "Text"
    assert res.artifacts["x"] == code


# from x.y import z
def test_nested_from_import(execute):
    code = """from matplotlib.pyplot import ylabel
x = ylabel('label')
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"].__class__.__name__ == "Text"
    assert res.artifacts["x"] == code


# from x.y import z as a
def test_nested_from_import_as(execute):
    code = """from matplotlib.pyplot import ylabel as yl
x = yl('label')
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"].__class__.__name__ == "Text"
    assert res.artifacts["x"] == code


# from x.y import *
def test_nested_from_import_starred(execute):
    code = """from matplotlib.pyplot import *
x = ylabel('label')
"""
    res = execute(code, artifacts=["x"])
    assert res.values["x"].__class__.__name__ == "Text"
    assert res.artifacts["x"] == code
