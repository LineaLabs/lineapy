from typing import List, Set

import pytest

from lineapy.system_tracing._function_calls_to_object_side_effects import (
    function_calls_to_object_side_effects,
)
from lineapy.system_tracing._object_side_effect import (
    ImplicitDependencyObject,
    MutatedObject,
    ViewOfObjects,
)
from lineapy.system_tracing.function_call import FunctionCall
from lineapy.utils.lineabuiltins import file_system, l_list
from tests.util import IsObject


def my_fn():
    pass


list_: List[object] = []
list_of_list = [list_]
set_: Set[object] = set()


@pytest.mark.parametrize(
    "function_calls,object_side_effects",
    [
        pytest.param(
            [FunctionCall(my_fn, [], {}, None)],
            [],
            id="unknown function",
        ),
        pytest.param(
            [FunctionCall(l_list, [list_], {}, list_of_list)],
            [ViewOfObjects([IsObject(list_of_list), IsObject(list_)])],
            id="view of result and all args",
        ),
        pytest.param(
            [FunctionCall(set_.add, [10], {}, set_)],
            [MutatedObject(IsObject(set_))],
            id="mutated self",
        ),
        pytest.param(
            [FunctionCall(open, [""], {}, None)],
            [ImplicitDependencyObject(file_system)],
            id="implicit dependency on external state",
        ),
    ],
)
def test_function_calls_to_object_side_effects(
    function_calls, object_side_effects, function_inspector
):
    assert list(
        function_calls_to_object_side_effects(
            function_inspector, function_calls
        )
    ) == list(object_side_effects)
