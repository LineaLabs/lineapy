import ast
import operator
from typing import cast, Any, Union, Optional

from lineapy import linea_publish
from lineapy.constants import LINEAPY_TRACER_NAME
from lineapy.instrumentation.tracer import Tracer
from lineapy.instrumentation.variable import Variable
from lineapy.lineabuiltins import __build_list__
from lineapy.transformer.transformer_util import (
    extract_concrete_syntax_from_node,
    get_call_function_name,
    get_tracer_ast_call_func,
    synthesize_linea_publish_call_ast,
    synthesize_tracer_call_ast,
    synthesize_tracer_headless_literal_ast,
    synthesize_tracer_headless_variable_ast,
    turn_none_to_empty_str,
)
from lineapy.utils import UserError, InvalidStateError


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

    def visit_Expr(self, node: ast.Expr) -> Any:
        """
        Exprs are indications that it's a new line
        """
        v = node.value
        if isinstance(v, ast.Name):
            return synthesize_tracer_headless_variable_ast(v)  # type: ignore
        elif isinstance(v, ast.Constant):
            return synthesize_tracer_headless_literal_ast(v)  # type: ignore
        return ast.Expr(value=self.visit(node.value))

    def visit_Import(self, node):
        """
        Similar to `visit_ImportFrom`, slightly different class syntax
        """
        result = []
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        for lib in node.names:
            result.append(
                ast.Expr(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(
                                id=LINEAPY_TRACER_NAME,
                                ctx=ast.Load(),
                            ),
                            attr="trace_import",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg="name",
                                value=ast.Constant(value=lib.name),
                            ),
                            ast.keyword(
                                arg="syntax_dictionary",
                                value=syntax_dictionary,
                            ),
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
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        keys = []
        values = []
        for alias in node.names:
            keys.append(ast.Constant(value=alias.name))
            # needed turn_none_to_empty_str because of some issue with pydantic
            values.append(ast.Constant(value=turn_none_to_empty_str(alias.asname)))

        result = ast.Expr(
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                    attr=Tracer.trace_import.__name__,
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value=node.module)),
                    ast.keyword(arg="syntax_dictionary", value=syntax_dictionary),
                    ast.keyword(
                        arg="attributes",
                        value=ast.Dict(keys=keys, values=values),
                    ),
                ],
            )
        )
        return result

    def visit_Name(self, node) -> ast.Call:
        return ast.Call(
            func=ast.Name(
                id=Variable.__name__,
                ctx=ast.Load(),
            ),
            args=[ast.Constant(value=node.id)],
            keywords=[],
        )

    def visit_Call(self, node) -> Union[ast.Call, ast.Expr]:
        """
        TODO: support key word
        TODO: find function_module
        """
        name_ref = get_call_function_name(node)
        # a little hacky, assume no one else would have a function name
        #   called linea_publish

        if name_ref["function_name"] == linea_publish.__name__:
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
            if not isinstance(node.args[0], ast.Name):
                raise UserError(
                    "Please pass a variable as the first argument to"
                    f" `{linea_publish.__name__}`"
                )
            var_node = cast(ast.Name, node.args[0])
            if len(node.args) == 2:
                if not isinstance(node.args[1], ast.Constant):
                    raise UserError(
                        "Please pass a string for the description as the"
                        " second argument to"
                        f" `{linea_publish.__name__}`, you gave"
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
            # code = self._get_code_from_node(node)
            argument_nodes = [self.visit(arg) for arg in node.args]
            return synthesize_tracer_call_ast(
                name_ref["function_name"], argument_nodes, node
            )

    def visit_Assign(self, node: ast.Assign) -> Union[ast.Expr, ast.Call]:
        """
        Note
        - some code segments subsume the others
        - need to pad with expr to make astor happy
        https://stackoverflow.com/questions/49646402/function-isnt-added-to-new-line-when-adding-node-to-ast-in-python
        """

        syntax_dictionary = extract_concrete_syntax_from_node(node)
        if isinstance(node.targets[0], ast.Subscript):
            # Assigning a specific value to an index
            subscript_target: ast.Subscript = node.targets[0]
            index = subscript_target.slice
            if not isinstance(index, ast.Constant) or isinstance(index, ast.Name):
                raise NotImplementedError(
                    "Assignment for Subscript supported only for Constant and"
                    " Name indices."
                )
            argument_nodes = [
                self.visit(subscript_target.value),
                self.visit(index),
                self.visit(node.value),
            ]
            return synthesize_tracer_call_ast(
                operator.setitem.__name__, argument_nodes, node
            )

        if not isinstance(node.targets[0], ast.Name):
            raise NotImplementedError("Other assignment types are not supported")

        variable_name = node.targets[0].id  # type: ignore
        call_ast = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.assign.__name__,
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
                    arg="syntax_dictionary",
                    value=syntax_dictionary,
                ),
            ],
        )
        result = ast.Expr(value=call_ast)
        return result

    def visit_List(self, node: ast.List) -> ast.Call:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return synthesize_tracer_call_ast(__build_list__.__name__, elem_nodes, node)

    def visit_BinOp(self, node: ast.BinOp) -> ast.Call:
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
        return synthesize_tracer_call_ast(op.__name__, argument_nodes, node)

    def visit_Subscript(self, node: ast.Subscript) -> ast.Call:
        # Currently only support Constant, Name, Tuples of Constant and Name.
        # TODO: support slices, e.g., x[1:2]
        args = []
        index = node.slice
        if isinstance(index, ast.Name) or isinstance(index, ast.Constant):
            args.append(self.visit(index))
        else:
            raise NotImplementedError("Subscript for multiple indices not supported.")
        if isinstance(node.ctx, ast.Load):
            args.insert(0, self.visit(node.value))
            return synthesize_tracer_call_ast(operator.getitem.__name__, args, node)
        elif isinstance(node.ctx, ast.Del):
            raise NotImplementedError("Subscript with ctx=ast.Del() not supported.")
        else:
            raise InvalidStateError(
                "Subscript with ctx=ast.Load() should have been handled by"
                " visit_Assign."
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """
        For now, assume the function is pure, i.e.:
        - no globals
        - no writing to variables defined outside the scope
        TODO: remove these limitations in future PRs
        """
        # apparently FunctionDef is not inside Expr so for the new call we need to create new line
        function_name = node.name
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        return ast.Expr(
            value=ast.Call(
                func=get_tracer_ast_call_func(Tracer.define_function.__name__),
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
                ],
            ),
        )

    def visit_Attribute(self, node: ast.Attribute) -> ast.Call:
        return synthesize_tracer_call_ast()
