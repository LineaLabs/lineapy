import ast
import operator
from typing import Optional, cast, Union, Any

from lineapy.constants import LINEAPY_PUBLISH_FUNCTION_NAME, LINEAPY_TRACER_NAME
from lineapy.instrumentation.tracer import Tracer
from lineapy.lineabuiltins import __build_list__
from lineapy.transformer.transformer_util import (
    get_call_function_name,
    synthesize_linea_publish_call_ast,
    synthesize_tracer_call_ast,
)
from lineapy.utils import UserError, InvalidStateError


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

    @staticmethod
    def _get_index(subscript: ast.Subscript) -> Any:
        if hasattr(subscript.slice, "value"):
            return subscript.slice.value
        return subscript.slice

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

    def visit_Assign(self, node: ast.Assign) -> Union[ast.Expr, ast.Call]:
        """
        Note
        - some code segments subsume the others
        - need to pad with expr to make astor happy
        https://stackoverflow.com/questions/49646402/function-isnt-added-to-new-line-when-adding-node-to-ast-in-python
        """
        code = self._get_code_from_node(node)
        if isinstance(node.targets[0], ast.Subscript):
            # Assigning a specific value to an index
            subscript_target: ast.Subscript = node.targets[0]
            index = self._get_index(subscript_target)
            # note: isinstance(index, ast.List) only works for pandas, not Python lists
            if (
                isinstance(index, ast.Constant)
                or isinstance(index, ast.Name)
                or isinstance(index, ast.List)
                or isinstance(index, ast.Slice)
            ):
                argument_nodes = [
                    self.visit(subscript_target.value),
                    self.visit(index),
                    self.visit(node.value),
                ]
                return synthesize_tracer_call_ast(
                    list.__setitem__.__name__, argument_nodes, code
                )

            raise NotImplementedError(
                "Assignment for Subscript supported only for Constant and Name indices."
            )
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

    def visit_List(self, node: ast.List) -> ast.Call:
        code = self._get_code_from_node(node)
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return synthesize_tracer_call_ast(__build_list__.__name__, elem_nodes, code)

    def visit_BinOp(self, node: ast.BinOp) -> ast.Call:
        code = self._get_code_from_node(node)
        ast_to_op_map = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.BitAnd: operator.and_,
            ast.MatMult: operator.matmul,
        }
        op = ast_to_op_map[node.op.__class__]
        argument_nodes = [self.visit(node.left), self.visit(node.right)]
        return synthesize_tracer_call_ast(op.__name__, argument_nodes, code)

    def visit_Slice(self, node: ast.Slice) -> ast.Call:
        code = self._get_code_from_node(node)
        slice_arguments = [self.visit(node.lower), self.visit(node.upper)]
        if node.step is not None:
            slice_arguments.append(self.visit(node.step))
        slice_call = synthesize_tracer_call_ast(slice.__name__, slice_arguments, code)
        getitem_arguments = [slice_call]
        return synthesize_tracer_call_ast(
            list.__getitem__.__name__, getitem_arguments, code
        )

    def visit_Subscript(self, node: ast.Subscript) -> ast.Call:
        code = self._get_code_from_node(node)
        args = []
        index = self._get_index(node)
        if (
            isinstance(index, ast.Name)
            or isinstance(index, ast.Constant)
            or isinstance(index, ast.List)
        ):
            args.append(self.visit(index))
        elif isinstance(index, ast.Slice):
            return synthesize_tracer_call_ast(
                list.__getitem__.__name__, [self.visit_Slice(index)], code
            )
        else:
            raise NotImplementedError("Subscript for multiple indices not supported.")
        if isinstance(node.ctx, ast.Load):
            args.insert(0, self.visit(node.value))
            return synthesize_tracer_call_ast(operator.getitem.__name__, args, code)
        elif isinstance(node.ctx, ast.Del):
            raise NotImplementedError("Subscript with ctx=ast.Del() not supported.")
        else:
            raise InvalidStateError(
                "Subscript with ctx=ast.Load() should have been handled by visit_Assign."
            )
