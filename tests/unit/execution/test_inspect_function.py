"""
Tests FunctionInspector().inspect to verify the right side effects are the same.
"""
from operator import setitem
from pickle import dump
from tempfile import NamedTemporaryFile
from types import SimpleNamespace

import numpy
import pandas
from pandas import DataFrame
from pytest import fixture, mark, param
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import create_engine

from lineapy.execution.inspect_function import FunctionInspector
from lineapy.instrumentation.annotation_spec import (
    BoundSelfOfFunction,
    ExternalState,
    ImplicitDependencyValue,
    MutatedValue,
    PositionalArg,
    Result,
    ViewOfValues,
)
from lineapy.utils.lineabuiltins import l_list

filename = NamedTemporaryFile().name
handle = open(filename, "wb")


@mark.parametrize(
    ("function", "args", "kwargs", "side_effects"),
    [
        param(
            setattr,
            (SimpleNamespace(), "x", "y"),
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
            (SimpleNamespace(), "x", []),
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
            ["/dev/null"],
            {},
            [
                MutatedValue(
                    mutated_value=ExternalState(external_state="file_system")
                )
            ],
            id="to_csv",
        ),
        param(
            dump,
            [{"lineapy": "hi"}, handle],
            {},
            [
                MutatedValue(
                    mutated_value=PositionalArg(positional_argument_index=1),
                )
            ],
            id="pickle.dump",
        ),
        param(
            set().add,
            (1,),
            {},
            [
                MutatedValue(
                    mutated_value=BoundSelfOfFunction(self_ref="SELF_REF")
                )
            ],
            id="set.add",
        ),
        param(
            RandomForestClassifier().fit,
            [[[1]], [2]],
            {},
            [
                MutatedValue(
                    mutated_value=BoundSelfOfFunction(self_ref="SELF_REF")
                ),
                ViewOfValues(
                    views=[
                        BoundSelfOfFunction(self_ref="SELF_REF"),
                        Result(result="RESULT"),
                    ]
                ),
            ],
            id="clf.fit",
        ),
        param(
            setitem,
            [{}, 1, []],
            {},
            [
                MutatedValue(
                    mutated_value=PositionalArg(positional_argument_index=0),
                ),
                ViewOfValues(
                    views=[
                        PositionalArg(positional_argument_index=2),
                        PositionalArg(positional_argument_index=0),
                    ]
                ),
            ],
            id="setitem",
        ),
        param(
            pandas.read_csv,
            ["tests/simple_data.csv"],
            {},
            [
                ImplicitDependencyValue(
                    dependency=ExternalState(external_state="file_system")
                )
            ],
            id="read_csv",
        ),
        param(
            pandas.read_csv("tests/simple_data.csv").drop,
            [0],
            {"inplace": True},
            [
                MutatedValue(
                    mutated_value=BoundSelfOfFunction(self_ref="SELF_REF")
                )
            ],
            id="inplace true",
        ),
        param(
            pandas.read_csv("tests/simple_data.csv").drop,
            [0],
            {"inplace": False},
            [],
            id="inplace false",
        ),
        param(
            l_list,
            [[], []],
            {},
            [
                ViewOfValues(
                    views=[
                        Result(result="RESULT"),
                        PositionalArg(positional_argument_index=0),
                        PositionalArg(positional_argument_index=1),
                    ]
                ),
            ],
            id="inplace false",
        ),
        param(
            pandas.DataFrame({"name": ["User 1", "User 2", "User 3"]}).to_sql,
            ["users"],
            {"con": create_engine("sqlite://", echo=False)},
            [MutatedValue(mutated_value=ExternalState(external_state="db"))],
            id="to_sql",
        ),
        param(numpy.add, [1, 2], {}, [], id="ufunc"),
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
