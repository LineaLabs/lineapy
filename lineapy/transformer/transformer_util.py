import ast
from typing import Any, Dict, List, Optional, cast
from dataclasses import dataclass
from astpretty import pprint

from lineapy.data.types import Node
from lineapy.utils import CaseNotHandledError
from lineapy.constants import LINEAPY_TRACER_NAME
from lineapy.instrumentation.tracer import Tracer

"""
AST synthesizers used by node_transformers
"""


SYNTAX_KEY = ["lineno", "col_offset", "end_lineno", "end_col_offset"]


# @dataclass
# class CodeSyntax:
#     lineno: int
#     col_offset: int
#     end_lineno: int
#     end_col_offset: int


def extract_concrete_syntax_from_node(ast_node) -> ast.Dict:
    """
    TODO: adding typing
    """
    # pprint(ast_node)
    return ast.Dict(
        keys=[ast.Constant(value=key) for key in SYNTAX_KEY],
        values=[
            ast.Constant(value=ast_node.__getattribute__(key)) for key in SYNTAX_KEY
        ],
    )

    # decided not to use the following to make code synthesis easier...
    # return CodeSyntax(
    #     lineno=ast_node.lineno,
    #     col_offset=ast_node.col_offset,
    #     end_lineno=ast_node.end_lineno,
    #     end_col_offset=ast_node.end_col_offset,
    # )


def turn_none_to_empty_str(a: Optional[str]):
    if not a:
        return ""
    return a


def get_call_function_name(node: ast.Call):
    if type(node.func) == ast.Name:
        func_name = cast(ast.Name, node.func)
        return {"function_name": func_name.id}
    if type(node.func) == ast.Attribute:
        func_attribute = cast(ast.Attribute, node.func)
        return {
            "function_name": func_attribute.attr,
            "function_module": func_attribute.value.id,
        }
    raise CaseNotHandledError("Other types of function calls!")


def synthesize_tracer_call_ast(
    function_name: str,
    argument_nodes: List[Any],
    syntax_dictionary: ast.Dict,  # FIXME
):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
            attr=Tracer.call.__name__,
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[
            ast.keyword(
                arg="function_name",
                value=ast.Constant(value=function_name),
            ),
            ast.keyword(
                arg="syntax_dictionary",
                value=syntax_dictionary,
            ),
            ast.keyword(
                arg="arguments",
                value=ast.List(elts=argument_nodes),
            ),
        ],
    )


def synthesize_linea_publish_call_ast(
    variable_name: str,
    description: Optional[str] = None,
):
    """
    TODO: add modules
    """
    keywords = [
        ast.keyword(
            arg="variable_name",
            value=ast.Constant(value=variable_name),
        )
    ]
    if description is not None:
        keywords.append(
            ast.keyword(
                arg="description",
                value=ast.Constant(value=description),
            )
        )
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
            attr=Tracer.publish.__name__,
            ctx=ast.Load(),
        ),
        args=[],
        keywords=keywords,
    )
