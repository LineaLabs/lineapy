from __future__ import annotations

import collections
import datetime
import enum
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Iterable, cast

from pydantic import BaseModel
from pydantic.fields import SHAPE_DICT, SHAPE_LIST

if TYPE_CHECKING:
    from lineapy.data.graph import Graph

from lineapy.data.types import (
    KeywordArgument,
    LineaID,
    NodeType,
    PositionalArgument,
    SourceCode,
)


@dataclass
class GraphPrinter:
    """
    Pretty prints a graph, in a similar way as how you would create it by hand.

    This representation should be consistant despite UUIDs being different.
    """

    graph: Graph

    # Whether to include the source locations from the graph
    include_source_location: bool = field(default=True)
    # Whether to print the ID fields for nodes
    include_id_field: bool = field(default=True)
    # Whether to include the session
    include_session: bool = field(default=True)
    # Whether to include the imports needed to run the file
    include_imports: bool = field(default=False)
    # Whether to include timing information
    include_timing: bool = field(default=True)

    # Set to True to nest node strings, when they only have one successor.
    nest_nodes: bool = field(default=True)
    id_to_attribute_name: Dict[LineaID, str] = field(default_factory=dict)

    # Mapping of each node types to the count of nodes of that type printed
    # so far to create variables based on node type.
    node_type_to_count: Dict[NodeType, int] = field(
        default_factory=lambda: collections.defaultdict(lambda: 0)
    )

    source_code_count: int = field(default=0)

    def print(self) -> str:
        return "\n".join(self.lines())

    def get_node_type_count(self, node_type: NodeType) -> int:
        prev = self.node_type_to_count[node_type]
        next = prev + 1
        self.node_type_to_count[node_type] = next
        return next

    def get_node_type_name(self, node_type: NodeType) -> str:
        return f"{pretty_print_node_type(node_type)}_{self.get_node_type_count(node_type)}"

    def lines(self) -> Iterable[str]:
        if self.include_imports:
            yield "import datetime"
            yield "from pathlib import *"
            yield "from lineapy.data.types import *"
            yield "from lineapy.utils.utils import get_new_id"
        if self.include_session:
            yield "session = ("
            yield from self.pretty_print_model(self.graph.session_context)
            yield ")"

        for node in self.graph.visit_order():
            node_id = node.id
            attr_name = self.get_node_type_name(node.node_type)

            # If the node has source code, and we haven't printed it before
            # print that first so it will just reference
            source_location = node.source_location
            if (
                source_location
                and source_location.source_code.id
                not in self.id_to_attribute_name
            ):
                self.source_code_count += 1
                name = f"source_{self.source_code_count}"
                self.id_to_attribute_name[
                    source_location.source_code.id
                ] = name
                yield f"{name} = ("
                yield from self.pretty_print_model(source_location.source_code)
                yield ")"
            # If the node only has one successor, then save its body
            # as the attribute name, so its inlined when accessed.
            if node.node_type == NodeType.ImportNode:
                # if node.name == "lineapy":  # type: ignore
                # do not track version change, pin to 0.0.1
                node.version = ""  # type: ignore

            if (
                self.nest_nodes
                and len(list(self.graph.nx_graph.successors(node_id))) == 1
            ):
                self.id_to_attribute_name[node_id] = "\n".join(
                    self.pretty_print_model(node)
                )

            else:
                yield f"{attr_name} = ("
                yield from self.pretty_print_model(node)
                yield ")"
                self.id_to_attribute_name[node_id] = attr_name

    def pretty_print_model(self, model: BaseModel) -> Iterable[str]:
        yield f"{type(model).__name__}("
        yield from self.pretty_print_node_lines(model)
        yield ")"

    def lookup_id(self, id: LineaID) -> str:
        if id in self.id_to_attribute_name:
            return self.id_to_attribute_name[id] + ".id"
        return repr(id)

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
            if k == "source_location" and not self.include_source_location:
                continue
            if k == "id" and not self.include_id_field:
                continue
            if k == "session_id" and not self.include_session:
                continue
            # don't print empty args, kwargs, or reads
            if (
                k
                in {
                    "positional_args",
                    "keyword_args",
                    "global_reads",
                    "implicit_dependencies",
                }
            ) and not v:
                continue
            if tp == LineaID and shape == SHAPE_LIST:
                args = [self.lookup_id(id_) for id_ in v]
                # Arguments are unordered and we need to sort them to
                #   make sure that the diffing do not create false negatives
                v_str = "[" + ", ".join(args) + "]"
            elif tp == PositionalArgument and shape == SHAPE_LIST:
                # special case for positional arguments here because we added starred args support.
                # the only difference will be an appearance of a star in front of the node reference
                # eg positional_args = [callnode.id] vs positional_args = [*callnode.id]
                args = [
                    id_.starred * "*" + str(self.lookup_id(id_.id))
                    for id_ in v
                ]
                # Arguments are unordered and we need to sort them to
                #   make sure that the diffing do not create false negatives
                v_str = "[" + ", ".join(args) + "]"
            elif tp == KeywordArgument and shape == SHAPE_LIST:
                # Sort kwargs on printing for consistant ordering
                args = [
                    f"{repr(kwa.key)}: {self.lookup_id(kwa.value)}"
                    for kwa in sorted(v, key=lambda x: x.key)
                ]
                v_str = "{" + ", ".join(args) + "}"
            elif tp == LineaID and shape == SHAPE_DICT:
                # Sort kwargs on printing for consistant ordering
                args = [
                    f"{repr(k)}: {self.lookup_id(id_)}"
                    for k, id_ in sorted(
                        cast(Dict[str, LineaID], v).items(), key=lambda x: x[0]
                    )
                ]
                v_str = "{" + ", ".join(args) + "}"
            # Singleton NewTypes get cast to str by pydantic, so we can't differentiate at the field
            # level between them and strings, so we just see if can look up the ID
            elif isinstance(v, str) and v in self.id_to_attribute_name:
                v_str = self.lookup_id(v)  # type: ignore
            elif isinstance(v, datetime.datetime) and not self.include_timing:
                continue
            else:
                v_str = "\n".join(self.pretty_print_value(v))
            yield f"{k}={v_str},"

    def pretty_print_value(self, v: object) -> Iterable[str]:
        if isinstance(v, SourceCode):
            yield self.lookup_id(v.id)
        elif isinstance(v, enum.Enum):
            yield f"{type(v).__name__}.{v.name}"
        elif isinstance(v, BaseModel):
            yield from self.pretty_print_model(v)
        elif isinstance(v, list):
            yield "["
            for x in v:
                yield from self.pretty_print_value(x)
                yield ","
            yield "]"
        elif isinstance(v, str):
            yield pretty_print_str(v)
        else:
            value = repr(v)
            # Try parsing as Python code, if we can't, then wrap in string.
            try:
                compile(value, "", "exec")
            except SyntaxError:
                value = repr(value)
            yield value


def pretty_print_str(s: str) -> str:
    """
    Pretty prints a string, so that if it has a newline, prints it as a triple
    quoted string.
    """
    if "\n" in s:
        string_escape_single_quote = s.replace("'", "\\'")
        return f"'''{string_escape_single_quote}'''"
    return repr(s)


def pretty_print_node_type(type: NodeType) -> str:
    """
    Turns a node type into something that can be used as a variable name.
    """
    return camel_to_snake_case(type.name.replace("Node", ""))


# https://stackoverflow.com/a/1176023/907060
camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake_case(s: str) -> str:
    return camel_case_pattern.sub("_", s).lower()
