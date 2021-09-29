from __future__ import annotations
from dataclasses import dataclass, field
import collections
from xml.dom import SyntaxErr
from lineapy.transformer.transformer_util import SYNTAX_KEY
from typing import TYPE_CHECKING, Iterable
from pydantic import BaseModel
import collections
import enum
import re
from pydantic.fields import SHAPE_LIST


if TYPE_CHECKING:
    from lineapy.data.graph import Graph
from lineapy.data.types import LineaID, NodeType
from lineapy.utils import prettify


@dataclass
class GraphPrinter:
    """
    Pretty prints a graph, in a similar way as how you would create it by hand.

    This representation should be consistant despite UUIDs being different.
    """

    graph: Graph

    """
    Set `snapshot_mode` to False if you want to see the ID values and
    not see the line numbers, which is helpful during debugging.
    """
    snapshot_mode: bool
    # Set to True to nest node strings, when they only have one successor.
    nest_nodes: bool = field(default=True)
    id_to_attribute_name: dict[LineaID, str] = field(default_factory=dict)

    # Mapping of each node types to the count of nodes of that type printed
    # so far to create variables based on node type.
    node_type_to_count: dict[NodeType, int] = field(
        default_factory=lambda: collections.defaultdict(lambda: 0)
    )

    def print(self) -> str:
        return prettify("\n".join(self.lines()))

    def get_node_type_count(self, node_type: NodeType) -> int:
        prev = self.node_type_to_count[node_type]
        next = prev + 1
        self.node_type_to_count[node_type] = next
        return next

    def get_node_type_name(self, node_type: NodeType) -> str:
        return f"{pretty_print_node_type(node_type)}_{self.get_node_type_count(node_type)}"

    def lines(self) -> Iterable[str]:
        yield "import datetime"
        yield "from lineapy.data.types import *"
        yield "from lineapy.utils import get_new_id"
        yield "session = ("
        yield from self.pretty_print_model(self.graph.session_context)
        yield ")"

        for node in self.graph.visit_order():
            node_id = node.id
            attr_name = self.get_node_type_name(node.node_type)
            # If the node only has one successor, then save its body
            # as the attribute name, so its inlined when accessed.
            if (
                self.nest_nodes
                and len(list(self.graph._nx_graph.successors(node_id))) == 1
            ):
                self.id_to_attribute_name[node_id] = "\n".join(
                    self.pretty_print_model(node)
                )

            else:
                self.id_to_attribute_name[node_id] = attr_name
                yield f"{attr_name} = ("
                yield from self.pretty_print_model(node)
                yield ")"

    def pretty_print_model(self, model: BaseModel) -> Iterable[str]:
        yield f"{type(model).__name__}("
        yield from self.pretty_print_node_lines(model)
        yield ")"

    def lookup_id(self, id: LineaID) -> str:
        return self.id_to_attribute_name[id] + ".id"

    def pretty_print_node_lines(self, node: BaseModel) -> Iterable[str]:
        for k in node.__fields__.keys():
            v = getattr(node, k)

            # Ignore nodes that are none
            if v is None:
                continue

            field = node.__fields__[k]
            tp = field.type_
            shape = field.shape
            v_str: str
            if k == "node_type":
                continue
            if k in SYNTAX_KEY and self.snapshot_mode is False:
                continue
            elif k == "id":
                v_str = "get_new_id()"
            elif k == "session_id":
                v_str = "session.id"
            elif tp == LineaID and shape == SHAPE_LIST and v is not None:
                args = [self.lookup_id(id_) for id_ in v]
                # Arguments are unordered, even though they are lists not sets,
                # so sort them before exporting
                if k == "arguments":
                    args.sort()
                v_str = "[" + ", ".join(args) + "]"
            # Singleton NewTypes get cast to str by pydantic, so we can't differentiate at the field
            # level between them and strings, so we just see if can look up the ID
            elif isinstance(v, str) and v in self.id_to_attribute_name:  # type: ignore
                v_str = self.lookup_id(v)  # type: ignore
            else:
                v_str = "\n".join(self.pretty_print_value(v))
            yield f"{k}={v_str},"

    def pretty_print_value(self, v: object) -> Iterable[str]:
        if isinstance(v, enum.Enum):
            yield f"{type(v).__name__}.{v.name}"
        elif isinstance(v, BaseModel):
            yield from self.pretty_print_model(v)
        elif isinstance(v, list):
            yield "["
            for x in v:
                yield from self.pretty_print_value(x)
                yield ","
            yield "]"
        else:
            value = repr(v)
            # Try parsing as Python code, if we can't, then wrap in string.
            try:
                compile(value, "", "exec")
            except SyntaxError:
                value = repr(value)
            yield value


def pretty_print_node_type(type: NodeType) -> str:
    """
    Turns a node type into something that can be used as a variable name.
    """
    return camel_to_snake_case(type.name.replace("Node", ""))


# https://stackoverflow.com/a/1176023/907060
camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake_case(s: str) -> str:
    return camel_case_pattern.sub("_", s).lower()
