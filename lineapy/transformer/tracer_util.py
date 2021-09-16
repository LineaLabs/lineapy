from typing import Any, Callable, List

from lineapy.utils import get_new_id
from lineapy.instrumentation.variable import Variable

from lineapy.data.types import ArgumentNode, CallNode, LineaID

# Created to avoid circular imports...


def create_argument_nodes(
    arguments: Any,
    session_context_id: LineaID,
    look_up_node_id_by_variable_name: Callable[[str], LineaID],
) -> List[ArgumentNode]:
    argument_nodes = []
    for idx, a in enumerate(arguments):
        if type(a) is int or type(a) is str:
            new_literal_arg = ArgumentNode(
                id=get_new_id(),
                session_id=session_context_id,
                value_literal=a,
                positional_order=idx,
            )
            argument_nodes.append(new_literal_arg)
        elif type(a) is CallNode:
            new_call_arg = ArgumentNode(
                id=get_new_id(),
                session_id=session_context_id,
                value_node_id=a.id,
                positional_order=idx,
            )
            argument_nodes.append(new_call_arg)
        elif type(a) is Variable:
            var_id = look_up_node_id_by_variable_name(a.name)
            new_variable_arg = ArgumentNode(
                id=get_new_id(),
                session_id=session_context_id,
                value_node_id=var_id,
                positional_order=idx,
            )
            argument_nodes.append(new_variable_arg)

        else:
            raise NotImplementedError(
                f"Haven't seen this argument type before: {type(a)}"
            )
    return argument_nodes
