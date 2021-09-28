import ast
from typing import List, Optional


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
    return {key: getattr(ast_node, key, None) for key in SYNTAX_KEY}
