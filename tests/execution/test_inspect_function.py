"""
Tests FunctionInspector().inspect to verify the right side effects are the same.
"""
import pytest

from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.annotation_spec import (
    MutatedValue,
    PositionalArg,
    ValuePointer,
    ViewOfValues,
)


@pytest.mark.parametrize(
    ("function", "args", "kwargs", "side_effects"),
    [
        pytest.param(
            setattr,
            (lambda: None, "x", "y"),
            {},
            [
                MutatedValue(
                    mutated_value=PositionalArg(positional_argument_index=0)
                )
            ],
            id="setattr immutable",
        ),
    ],
)
def test_inspect(
    function_inspector: FunctionInspector, function, args, kwargs, side_effects
):
    result = function(*args, **kwargs)
    assert (
        list(function_inspector.inspect(function, args, kwargs, result))
        == side_effects
    )


# Make a session scoped fixture for the function inspector so its instatation
# is cached for all the tests
@pytest.fixture(scope="session")
def function_inspector():
    return FunctionInspector()
