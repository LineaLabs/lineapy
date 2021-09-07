import ast
from lineapy.utils import CaseNotHandledError
from typing import Any, List, Optional, cast

from lineapy.constants import LINEAPY_TRACER_NAME
from lineapy.instrumentation.tracer import Tracer

"""
AST synthesizers used by node_transformers
"""


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
    code: str,
):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
            attr=Tracer.TRACE_CALL,
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[
            ast.keyword(
                arg="function_name",
                value=ast.Constant(value=function_name),
            ),
            ast.keyword(
                arg="code",
                value=ast.Constant(value=code),
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
            attr=Tracer.TRACE_PUBLISH,
            ctx=ast.Load(),
        ),
        args=[],
        keywords=keywords,
    )
