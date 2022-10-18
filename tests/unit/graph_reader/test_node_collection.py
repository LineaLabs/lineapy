from typing import List, Set

import pytest

from lineapy.graph_reader.node_collection import UserCodeNodeCollection
from lineapy.graph_reader.program_slice import get_slice_graph
from lineapy.instrumentation.tracer import Tracer


def get_user_code_nodecollection(
    input_code,
    execute,
    variable_sinks: Set[str],
    nc_name: str,
    input_variables: List[str],
    return_variables: List[str],
):
    tracer: Tracer = execute(input_code, snapshot=False)

    session_graph = tracer.graph
    session_id = tracer.tracer_context.session_context.id

    session_vars = tracer.db.get_variables_for_session(session_id)

    sink_node_id_list = [
        node_id for node_id, var in session_vars if var in variable_sinks
    ]

    sliced_graph = get_slice_graph(session_graph, sink_node_id_list)

    nc = UserCodeNodeCollection(
        set([node.id for node in sliced_graph.nodes]),
        session_graph,
        nc_name,
        input_variables=set(input_variables),
        return_variables=return_variables,
    )
    return nc


@pytest.mark.parametrize(
    "input_code, variable_sinks, nc_name, input_variables, return_variables",
    [
        [
            """
a = 2
p = "p"
b = p*a
""",
            ["p"],
            "test_nc",
            ["a", "b", "c"],
            ["y", "z"],
        ],
    ],
)
def test_fixture(
    execute,
    input_code,
    variable_sinks,
    nc_name,
    input_variables,
    return_variables,
):
    """
    Test the module generated from ArtifactCollection can run with/without
    input parameters
    """

    nc = get_user_code_nodecollection(
        input_code,
        execute,
        variable_sinks,
        nc_name,
        input_variables,
        return_variables,
    )

    expected_input_block = ", ".join(input_variables)
    expected_return_block = ", ".join(return_variables)
    expected_function_def = f"""def get_{nc_name}({expected_input_block}):
    p = "p"
    return {expected_return_block}"""
    assert expected_function_def == nc.get_function_definition()
