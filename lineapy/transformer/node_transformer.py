import ast
from typing import Optional, cast, Any

from lineapy.constants import LINEAPY_PUBLISH_FUNCTION_NAME, LINEAPY_TRACER_NAME
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.transformer_util import (
    get_call_function_name,
    synthesize_linea_publish_call_ast,
    synthesize_tracer_call_ast,
)
from lineapy.utils import UserError
from lineapy.lineabuiltins import __build_list__


def turn_none_to_empty_str(a: Optional[str]):
    if not a:
        return ""
    return a


class NodeTransformer(ast.NodeTransformer):
    """
    Notes:
    - Need to be careful about the order by which these calls are invoked
      so that the transformation do not get called more than once.
    """

    def __init__(self, source: str):
        self.source = source

    def _get_code_from_node(self, node):
        code = """{}""".format(ast.get_source_segment(self.source, node))
        return code

    def visit_Import(self, node):
        """
        Similar to `visit_ImportFrom`, slightly different class syntax
        """
        result = []
        code = self._get_code_from_node(node)
        for lib in node.names:
            result.append(
                ast.Expr(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                            attr="trace_import",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(arg="name", value=ast.Constant(value=lib.name)),
                            ast.keyword(arg="code", value=ast.Constant(value=code)),
                            ast.keyword(
                                arg="alias",
                                value=ast.Constant(value=lib.asname),
                            ),
                        ],
                    )
                )
            )
        return result

    def visit_ImportFrom(self, node):
        """ """
        keys = []
        values = []
        for alias in node.names:
            keys.append(ast.Constant(value=alias.name))
            # needed turn_none_to_empty_str because of some issue with pydantic
            values.append(ast.Constant(value=turn_none_to_empty_str(alias.asname)))

        code = self._get_code_from_node(node)
        result = ast.Expr(
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                    attr=Tracer.TRACE_IMPORT,
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value=node.module)),
                    ast.keyword(arg="code", value=ast.Constant(value=code)),
                    ast.keyword(
                        arg="attributes",
                        value=ast.Dict(keys=keys, values=values),
                    ),
                ],
            )
        )
        return result

    def visit_Call(self, node) -> ast.Call:
        """
        TODO: support key word
        TODO: find function_module
        """
        name_ref = get_call_function_name(node)
        # a little hacky, assume no one else would have a function name
        #   called linea_publish

        if name_ref["function_name"] == LINEAPY_PUBLISH_FUNCTION_NAME:
            # assume that we have two string inputs, else yell at the user
            if len(node.args) == 0:
                raise UserError(
                    "Linea publish requires at least the variable that you wish"
                    " to publish"
                )
            if len(node.args) > 2:
                raise UserError(
                    "Linea publish can take at most the variable name and the"
                    " description"
                )
            # TODO: support keyword arguments as well
            if type(node.args[0]) is not ast.Name:
                raise UserError(
                    "Please pass a variable as the first argument to"
                    f" `{LINEAPY_PUBLISH_FUNCTION_NAME}`"
                )
            var_node = cast(ast.Name, node.args[0])
            if len(node.args) == 2:
                if type(node.args[1]) is not ast.Constant:
                    raise UserError(
                        "Please pass a string for the description as the"
                        " second argument to"
                        f" `{LINEAPY_PUBLISH_FUNCTION_NAME}`, you gave"
                        f" {type(node.args[1])}"
                    )
                description_node = cast(ast.Constant, node.args[1])
                return synthesize_linea_publish_call_ast(
                    var_node.id, description_node.value
                )
            else:
                return synthesize_linea_publish_call_ast(var_node.id)
        else:
            # this is the normal case
            code = self._get_code_from_node(node)
            argument_nodes = [self.visit(arg) for arg in node.args]
            return synthesize_tracer_call_ast(
                name_ref["function_name"], argument_nodes, code
            )

    def visit_Assign(self, node: ast.Assign) -> ast.Expr:
        """
        Note
        - some code segments subsume the others
        - need to pad with expr to make astor happy
        https://stackoverflow.com/questions/49646402/function-isnt-added-to-new-line-when-adding-node-to-ast-in-python
        """
        code = self._get_code_from_node(node)
        if type(node.targets[0]) is not ast.Name:
            raise NotImplementedError("Other assignment types are not supported")
        variable_name = node.targets[0].id  # type: ignore
        call_ast = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.TRACE_ASSIGN,
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(
                    arg="variable_name",
                    value=ast.Constant(value=variable_name),
                ),
                ast.keyword(
                    arg="value_node",
                    value=self.visit(node.value),
                ),
                ast.keyword(
                    arg="code",
                    value=ast.Constant(value=code),
                ),
            ],
        )
        result = ast.Expr(value=call_ast)
        return result

    def visit_List(self, node: ast.List) -> Any:
        code = self._get_code_from_node(node)
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return synthesize_tracer_call_ast(__build_list__.__name__, elem_nodes, code)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        code = self._get_code_from_node(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        code = self._get_code_from_node(node)
