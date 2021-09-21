from typing import Callable, List, Union, Iterable

from lineapy.utils import get_new_id
from lineapy.instrumentation.variable import Variable

from lineapy.data.types import ArgumentNode, CallNode, LineaID

# Created to avoid circular imports...

ARG_TYPE = Union[int, float, str, bool, CallNode, Variable]
ARGS_TYPE = list[ARG_TYPE]
KEYWORD_ARGS_TYPE = list[tuple[str, ARG_TYPE]]


def create_argument_nodes(
    arguments: ARGS_TYPE,
    keyword_arguments: KEYWORD_ARGS_TYPE,
    session_context_id: LineaID,
    look_up_node_id_by_variable_name: Callable[[str], LineaID],
) -> List[ArgumentNode]:
    argument_nodes = []
    for idx_or_name, a in [*list(enumerate(arguments)), *keyword_arguments]:
        new_arg = ArgumentNode(
            id=get_new_id(),
            session_id=session_context_id,
        )
        if isinstance(idx_or_name, int):
            new_arg.positional_order = idx_or_name
        else:
            new_arg.keyword = idx_or_name  # type: ignore
        argument_nodes.append(new_arg)

        # TODO: Move to helper function
        if isinstance(a, (int, str, float, bool)):
            new_arg.value_literal = a
        elif type(a) is CallNode:
            new_arg.value_node_id = a.id
        elif type(a) is Variable:
            var_id = look_up_node_id_by_variable_name(a.name)
            new_arg.value_node_id = var_id
        else:
            raise NotImplementedError(
                f"Haven't seen this argument type before: {type(a)}"
            )

    return argument_nodes
