import pytest

# SS: small hack to prevent syrupy from using the entire code inside filename:
# SS: pass the code as a list of string of length 1
# list of the format: (testname,[code],[(asserttype,varname,expectedvalue)])
TESTS_CASES = [
    (
        "import_multiple_with_alias",
        [
            """from math import pow as power, sqrt as root
a = power(5, 2)
b = root(a)
"""
        ],
        [("value", "a", 25), ("value", "b", 5)],
    ),
    (
        "PIL_import_issue",
        [
            """from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")"""
        ],
        [("classname", "e", "PngImageFile")],
    ),
    (
        "import_multiple_without_alias",
        [
            """import pandas, numpy
c = pandas.DataFrame()
d = numpy.array([1,2,3])
"""
        ],
        [("classname", "c", "DataFrame"), ("valuearray", "d", [1, 2, 3])],
    ),
]


@pytest.mark.parametrize("_testname, code, asserts", TESTS_CASES)
def test_import(execute, assertionist, _testname, code, asserts):
    res = execute(code[0])
    assertionist(res, asserts)
