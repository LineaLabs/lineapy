import pytest

TESTS_CASES = [
    (
        [
            """a = 10
b = lambda x: x + 10
c = b(a)
"""
        ],
        [("value", "c", 20)],
    )
]


@pytest.mark.xfail
@pytest.mark.parametrize("code, asserts", TESTS_CASES)
def test_import(execute, assertionist, code, asserts):
    res = execute(code[0])
    assertionist(res, asserts)
