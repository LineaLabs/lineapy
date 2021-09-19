import ast
from typing import Any, List, Optional, cast

from lineapy.constants import (
    LINEAPY_TRACER_NAME,
    FUNCTION_NAME,
    FUNCTION_MODULE,
    SYNTAX_DICTIONARY,
    ARGUMENTS,
    VARIABLE_NAME,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils import CaseNotHandledError

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
        return {FUNCTION_NAME: func_name.id}
    if type(node.func) == ast.Attribute:
        func_attribute = cast(ast.Attribute, node.func)
        return {
            FUNCTION_NAME: func_attribute.attr,
            FUNCTION_MODULE: func_attribute.value.id,
        }
    raise CaseNotHandledError("Other types of function calls!")


def get_tracer_ast_call_func(tracer_func: str):
    return ast.Attribute(
        value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
        attr=tracer_func,
        ctx=ast.Load(),
    )


def synthesize_tracer_call_ast(
    function_name: str,
    argument_nodes: List[Any],
    node: Any,  # NOTE: not sure if the ast Nodes have a union type
    function_module: Optional[Any] = None,
):
    """
    Node is passed to synthesize the `syntax_dictionary`
      this reduces duplicate logic across the visit_* functions
    """

    syntax_dictionary = extract_concrete_syntax_from_node(node)
    call = ast.Call(
        func=get_tracer_ast_call_func(Tracer.call.__name__),
        args=[],
        keywords=[
            ast.keyword(
                arg=FUNCTION_NAME,
                value=ast.Constant(value=function_name),
            ),
            ast.keyword(
                arg=SYNTAX_DICTIONARY,
                value=syntax_dictionary,
            ),
            ast.keyword(
                arg=ARGUMENTS,
                value=ast.List(elts=argument_nodes, ctx=ast.Load()),
            ),
        ],
    )

    if function_module is not None:
        call.keywords.append(
            ast.keyword(
                arg=FUNCTION_MODULE,
                value=function_module,
            )
        )

    return call


def synthesize_tracer_headless_literal_ast(node: ast.Constant):
    """
    Similar to `synthesize_tracer_headless_variable_ast`, but for literals.
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
    Note that this was special cased from visit_Expr, so
      we need to create new line, including Expr
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
    artifact_name: Optional[str] = None,
):
    """
    Helper function for `tracer.publish`.
    Note that we do not need a new line because the original call would be
      wrapped in an Expr to begin with.
    """
    keywords = [
        ast.keyword(
            arg=VARIABLE_NAME,
            value=ast.Constant(value=variable_name),
        )
    ]
    if artifact_name is not None:
        keywords.append(
            ast.keyword(
                arg="description",
                value=ast.Constant(value=artifact_name),
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
