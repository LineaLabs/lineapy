"""
Tests FunctionInspector().inspect to verify the right side effects are the same.
"""
from pandas import DataFrame
from pytest import fixture, mark, param

from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.annotation_spec import (
    ExternalState,
    MutatedValue,
    PositionalArg,
    ViewOfValues,
)


@mark.parametrize(
    ("function", "args", "kwargs", "side_effects"),
    [
        param(
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
        param(
            setattr,
            (lambda: None, "x", []),
            {},
            [
                MutatedValue(
                    mutated_value=PositionalArg(positional_argument_index=0)
                ),
                ViewOfValues(
                    views=[
                        PositionalArg(positional_argument_index=2),
                        PositionalArg(positional_argument_index=0),
                    ]
                ),
            ],
            id="setattr mutable",
        ),
        param(
            DataFrame.from_records([]).to_csv,
            ("path"),
            {},
            [
                MutatedValue(
                    mutated_value=ExternalState(external_state="file_system")
                )
            ],
            id="to_csv",
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
@fixture(scope="session")
def function_inspector():
    return FunctionInspector()
