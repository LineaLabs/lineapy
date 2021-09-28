import ast
from typing import Any, List, Optional, Union

from lineapy.data.types import CallNode, Node
from lineapy.instrumentation.tracer import Tracer

"""
AST synthesizers used by node_transformers
"""

SYNTAX_KEY = ["lineno", "col_offset", "end_lineno", "end_col_offset"]


def create_lib_attributes(names: List[ast.alias]) -> dict[str, str]:
    return {
        alias.asname if alias.asname else alias.name: alias.name
        for alias in names
    }


def extract_concrete_syntax_from_node(
    ast_node: ast.AST,
) -> dict[str, Optional[int]]:
    """
    TODO: adding typing
    """
    # pprint(ast_node)
    return {key: getattr(ast_node, key, None) for key in SYNTAX_KEY}


def tracer_call_with_syntax(
    tracer: Tracer,
    function_name: str,
    argument_nodes: List[Node],
    node: ast.AST,
    function_module: Union[str, Node, None] = None,
    keyword_arguments: list[tuple[str, Node]] = [],
) -> CallNode:
    """
    Node is passed to synthesize the `syntax_dictionary`
      this reduces duplicate logic across the visit_* functions
    """

    syntax_dictionary = extract_concrete_syntax_from_node(node)
    return tracer.call(
        function_name,
        argument_nodes,
        keyword_arguments,
        syntax_dictionary,
        function_module,
    )
