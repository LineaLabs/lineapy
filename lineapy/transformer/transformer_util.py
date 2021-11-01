import ast
from typing import Dict, List

"""
AST synthesizers used by node_transformers
"""


def create_lib_attributes(names: List[ast.alias]) -> Dict[str, str]:
    return {
        alias.asname if alias.asname else alias.name: alias.name
        for alias in names
    }
