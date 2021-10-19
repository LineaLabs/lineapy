import pytest

TESTS_CASES_ARTIFACTS = [
    (
        [
            """b=30
def foo(a):
    return a - 10
c = foo(b)
"""
        ],
        [
            ("value", "c", 20),
            (
                "artifact",
                "c",
                """b=30
def foo(a):
    return a - 10
c = foo(b)
""",
            ),
        ],
    ),
]

TESTS_CASES_ARTIFACTS_FAILING = [
    (
        [
            """b=10
def foo(a):
    return a - b
c = foo(15)
"""
        ],
        [
            ("value", "c", 5),
            (
                "artifact",
                "c",
                """b=10
def foo(a):
    return a - b
c = foo(15)
""",
            ),
        ],
    ),
]


@pytest.mark.parametrize("code, asserts", TESTS_CASES_ARTIFACTS)
def test_function_definition_without_side_effect_artifacts(
    execute, assertionist, code, asserts
):
    res = execute(code[0], artifacts=["c"])
    assertionist(res, asserts)


@pytest.mark.xfail
@pytest.mark.parametrize("code, asserts", TESTS_CASES_ARTIFACTS_FAILING)
def test_function_definition_with_globals(
    execute, assertionist, code, asserts
):
    res = execute(code[0], artifacts=["c"])
    assertionist(res, asserts)
