import ast

"""
AST synthesizers used by node_transformers
"""

SYNTAX_KEY = ["lineno", "col_offset", "end_lineno", "end_col_offset"]


def create_lib_attributes(names: list[ast.alias]) -> dict[str, str]:
    return {
        alias.asname if alias.asname else alias.name: alias.name
        for alias in names
    }
