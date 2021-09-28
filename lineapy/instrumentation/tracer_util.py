from typing import Iterator

from lineapy.utils import get_new_id
from lineapy.data.types import (
    ArgumentNode,
    LineaID,
    Node,
)


def create_argument_nodes(
    arguments: list[Node],
    keyword_arguments: dict[str, Node],
    session_context_id: LineaID,
) -> Iterator[ArgumentNode]:
    for idx, v in enumerate(arguments):
        yield ArgumentNode(
            id=get_new_id(),
            session_id=session_context_id,
            positional_order=idx,
            value_node_id=v.id,
        )
    for k, v in keyword_arguments.items():
        yield ArgumentNode(
            id=get_new_id(),
            session_id=session_context_id,
            keyword=k,
            value_node_id=v.id,
        )
