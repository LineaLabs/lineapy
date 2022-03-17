from typing import List, Mapping

import pytest

from lineapy.data.types import LineaID
from lineapy.execution.side_effects import (
    ID,
    ImplicitDependencyNode,
    MutatedNode,
    SideEffects,
    Variable,
    ViewOfNodes,
)
from lineapy.system_tracing._object_side_effect import (
    ImplicitDependencyObject,
    MutatedObject,
    ObjectSideEffect,
    ViewOfObjects,
)
from lineapy.system_tracing._object_side_effects_to_side_effects import (
    object_side_effects_to_side_effects,
)
from lineapy.utils.lineabuiltins import file_system

list_: List[object] = []
list_1: List[object] = []


@pytest.mark.parametrize(
    "object_side_effects,input_nodes,output_globals,side_effects",
    [
        pytest.param(
            [MutatedObject(list_)],
            {"list_id": list_},
            {},
            [MutatedNode(ID(LineaID("list_id")))],
            id="mutated input",
        ),
        pytest.param(
            [ViewOfObjects([list_, list_1])],
            {"list_id": list_},
            {"output_list": list_1},
            [ViewOfNodes([ID(LineaID("list_id")), Variable("output_list")])],
            id="view of input and output",
        ),
        pytest.param(
            [ImplicitDependencyObject(file_system)],
            {},
            {},
            [ImplicitDependencyNode(file_system)],
            id="implicit dependency",
        ),
        pytest.param(
            [ViewOfObjects([list_, list_1, 10, 100])],
            {"list_id": list_},
            {"output_list": list_1},
            [ViewOfNodes([ID(LineaID("list_id")), Variable("output_list")])],
            id="views omit intermediates",
        ),
        pytest.param(
            [ViewOfObjects([list_, list_1, 10, 100])],
            {"list_id": list_},
            {},
            [],
            id="small views trimmed",
        ),
        pytest.param(
            [ViewOfObjects([list_, list_1]), MutatedObject(list_1)],
            {"list_id": list_},
            {"output_list": list_1},
            [
                MutatedNode(ID(LineaID("list_id"))),
                ViewOfNodes([ID(LineaID("list_id")), Variable("output_list")]),
            ],
            id="mutation after views",
        ),
        pytest.param(
            [MutatedObject(list_1), ViewOfObjects([list_, list_1])],
            {"list_id": list_},
            {"output_list": list_1},
            [ViewOfNodes([Variable("output_list"), ID(LineaID("list_id"))])],
            id="mutation before views",
        ),
    ],
)
def test_object_side_effects_to_side_effects(
    object_side_effects: List[ObjectSideEffect],
    input_nodes: Mapping[LineaID, object],
    output_globals: Mapping[str, object],
    side_effects: SideEffects,
):
    assert (
        list(
            object_side_effects_to_side_effects(
                object_side_effects,
                input_nodes,
                output_globals,
            )
        )
        == side_effects
    )
