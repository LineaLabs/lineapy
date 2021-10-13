import ast

"""
AST synthesizers used by node_transformers
"""


def create_lib_attributes(names: list[ast.alias]) -> dict[str, str]:
    return {
        alias.asname if alias.asname else alias.name: alias.name
        for alias in names
    }
