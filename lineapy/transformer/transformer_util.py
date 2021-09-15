import ast
from typing import Any, List, Optional, cast

from lineapy.utils import CaseNotHandledError
from lineapy.constants import LINEAPY_TRACER_NAME
from lineapy.instrumentation.tracer import Tracer

"""
AST synthesizers used by node_transformers
"""


SYNTAX_KEY = ["lineno", "col_offset", "end_lineno", "end_col_offset"]


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


def turn_none_to_empty_str(a: Optional[str]):
    if not a:
        return ""
    return a


def get_call_function_name(node: ast.Call) -> dict:
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
    node: Any,  # NOTE: not sure if the ast Nodes have a union type
):
    """
    Node is passed to synthesize the `syntax_dictionary`
      this reduces duplicate logic across the visit_* functions
    """

    syntax_dictionary = extract_concrete_syntax_from_node(node)
    call = ast.Call(
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
    return call


def synthesize_tracer_headless_literal_ast(node: ast.Constant):
    """
    NOTE:
    - this is definitely a new line, so including the Expr
    """
    syntax_dictionary = extract_concrete_syntax_from_node(node)
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.headless_literal.__name__,
                ctx=ast.Load(),
            ),
            args=[node, syntax_dictionary],
            keywords=[],
        )
    )


def synthesize_tracer_headless_variable_ast(node: ast.Name):
    """
    Either literal or a variable.
    NOTE:
    - definitely new line, including Expr
    """
    syntax_dictionary = extract_concrete_syntax_from_node(node)
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.headless_variable.__name__,
                ctx=ast.Load(),
            ),
            args=[ast.Constant(value=node.id), syntax_dictionary],
            keywords=[],
        )
    )


def synthesize_linea_publish_call_ast(
    variable_name: str,
    description: Optional[str] = None,
):
    """
    NOTE:
    - assume new line
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
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.publish.__name__,
                ctx=ast.Load(),
            ),
            args=[],
            keywords=keywords,
        )
    )
