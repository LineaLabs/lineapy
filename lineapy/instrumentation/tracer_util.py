from typing import Callable, List, Union, Iterable

from lineapy.utils import get_new_id

from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    LineaID,
    LiteralNode,
    Node,
    VariableNode,
)

# Created to avoid circular imports...

ARG_TYPE = Node
ARGS_TYPE = list[ARG_TYPE]
KEYWORD_ARGS_TYPE = list[tuple[str, ARG_TYPE]]


def create_argument_nodes(
    arguments: ARGS_TYPE,
    keyword_arguments: KEYWORD_ARGS_TYPE,
    session_context_id: LineaID,
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

        new_arg.value_node_id = a.id

    return argument_nodes
