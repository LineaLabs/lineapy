import ast
from typing import cast, Any

from lineapy import linea_publish
from lineapy.constants import (
    LINEAPY_TRACER_NAME,
    ADD,
    SUB,
    MULT,
    DIV,
    FLOORDIV,
    MOD,
    POW,
    LSHIFT,
    RSHIFT,
    BITOR,
    BITXOR,
    BITAND,
    MATMUL,
    EQ,
    NOTEQ,
    LT,
    LTE,
    GT,
    GTE,
    IS,
    NOT,
    ISNOT,
    IN,
    GET_ITEM,
    SET_ITEM,
    GETATTR,
    FUNCTION_NAME,
    FUNCTION_MODULE,
    SYNTAX_DICTIONARY,
    VARIABLE_NAME,
)
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
from lineapy.utils import UserError, InvalidStateError, info_log


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
    def _get_index(subscript: ast.Subscript) -> ast.AST:
        if isinstance(subscript.slice, ast.Index):
            return subscript.slice.value  # type: ignore
        return subscript.slice

    def visit_Expr(self, node: ast.Expr) -> Any:
        """
        NOTE
        - Exprs are indications that it's a new line, which allows us to
          observe headless variables and literals, which is useful for
          notebook settings.
        - Some expressions, like Assign, do not come with Expr wrapped
          and we need to pad with expr to correctly create new lines.
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
                            attr=Tracer.trace_import.__name__,
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg="name",
                                value=ast.Constant(value=lib.name),
                            ),
                            ast.keyword(
                                arg=SYNTAX_DICTIONARY,
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
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        keys = []
        values = []
        for alias in node.names:
            keys.append(ast.Constant(value=alias.name))
            # needed turn_none_to_empty_str because of some issue with pydantic
            values.append(
                ast.Constant(value=turn_none_to_empty_str(alias.asname))
            )

        result = ast.Expr(
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                    attr=Tracer.trace_import.__name__,
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(
                        arg="name", value=ast.Constant(value=node.module)
                    ),
                    ast.keyword(arg=SYNTAX_DICTIONARY, value=syntax_dictionary),
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

    def visit_Call(self, node) -> ast.Call:
        """
        TODO: support key word
        TODO: find function_module
        """
        name_ref = get_call_function_name(node)
        # a little hacky, assume no one else would have a function name
        #   called linea_publish
        if name_ref[FUNCTION_NAME] == linea_publish.__name__:
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
        else:  # this is the normal case, non-publish
            argument_nodes = [self.visit(arg) for arg in node.args]
            # TODO: support keyword arguments as well
            function_module = (
                ast.Constant(value=name_ref[FUNCTION_MODULE])
                if FUNCTION_MODULE in name_ref
                else None
            )
            return synthesize_tracer_call_ast(
                name_ref[FUNCTION_NAME],
                argument_nodes,
                node,
                function_module=function_module,
            )

    def visit_Assign(self, node: ast.Assign) -> ast.Expr:
        """
        Assign currently special cases for:
        - Subscript, e.g., `ls[0] = 1`
        - Constant, e.g., `a = 1`
        - Call, e.g., `a = foo()`

        TODO
        - Name, e.g. `a = b`
        """

        syntax_dictionary = extract_concrete_syntax_from_node(node)
        if isinstance(node.targets[0], ast.Subscript):
            # Assigning a specific value to an index
            subscript_target: ast.Subscript = node.targets[0]
            index = self._get_index(subscript_target)
            # note: isinstance(index, ast.List) only works for pandas,
            #  not Python lists
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
                call: ast.Call = synthesize_tracer_call_ast(
                    SET_ITEM,
                    argument_nodes,
                    node,
                )
                return ast.Expr(value=call)

            raise NotImplementedError(
                "Assignment for Subscript supported only for Constant and Name"
                " indices."
            )

        variable_name = node.targets[0].id  # type: ignore
        # Literal assign
        if isinstance(node.value, ast.Constant):
            call_ast: ast.Call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                    attr=Tracer.literal.__name__,
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(
                        arg="assigned_variable_name",
                        value=ast.Constant(value=variable_name),
                    ),
                    ast.keyword(
                        arg="value",
                        value=self.visit(node.value),
                    ),
                    ast.keyword(
                        arg=SYNTAX_DICTIONARY,
                        value=syntax_dictionary,
                    ),
                ],
            )
            return ast.Expr(value=call_ast)

        if not isinstance(node.targets[0], ast.Name):
            raise NotImplementedError(
                "Other assignment types are not supported"
            )

        call_ast = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.assign.__name__,
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(
                    arg=VARIABLE_NAME,
                    value=ast.Constant(value=variable_name),
                ),
                ast.keyword(
                    arg="value_node",
                    value=self.visit(node.value),
                ),
                ast.keyword(
                    arg=SYNTAX_DICTIONARY,
                    value=syntax_dictionary,
                ),
            ],
        )
        result = ast.Expr(value=call_ast)
        return result

    def visit_List(self, node: ast.List) -> ast.Call:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return synthesize_tracer_call_ast(
            __build_list__.__name__, elem_nodes, node
        )

    def visit_BinOp(self, node: ast.BinOp) -> ast.Call:
        ast_to_op_map = {
            ast.Add: ADD,
            ast.Sub: SUB,
            ast.Mult: MULT,
            ast.Div: DIV,
            ast.FloorDiv: FLOORDIV,
            ast.Mod: MOD,
            ast.Pow: POW,
            ast.LShift: LSHIFT,
            ast.RShift: RSHIFT,
            ast.BitOr: BITOR,
            ast.BitXor: BITXOR,
            ast.BitAnd: BITAND,
            ast.MatMult: MATMUL,
        }
        op = ast_to_op_map[node.op.__class__]
        argument_nodes = [self.visit(node.left), self.visit(node.right)]
        return synthesize_tracer_call_ast(
            op,
            argument_nodes,
            node,
        )

    def visit_Compare(self, node: ast.Compare) -> ast.Call:
        ast_to_op_map = {
            ast.Eq: EQ,
            ast.NotEq: NOTEQ,
            ast.Lt: LT,
            ast.LtE: LTE,
            ast.Gt: GT,
            ast.GtE: GTE,
            ast.Is: IS,
            ast.IsNot: ISNOT,
            ast.In: IN,
        }

        from copy import deepcopy

        # ast.Compare can have an arbitrary number of operators
        # e.g., a < b <= c
        left = self.visit(node.left)
        for i in range(len(node.ops)):
            op = node.ops[i]
            right = self.visit(node.comparators[i])
            tmp = deepcopy(left)
            if isinstance(op, ast.In) or isinstance(op, ast.NotIn):
                # flip left and right since in(a, b) = b.contains(a)
                left = right
                right = tmp
            if op.__class__ in ast_to_op_map:
                left = synthesize_tracer_call_ast(
                    ast_to_op_map[op.__class__],
                    [left, right],
                    node,
                )
            elif isinstance(op, ast.NotIn):
                # need to call operator.not_ on __contains___
                inside = synthesize_tracer_call_ast(
                    ast_to_op_map[ast.In],
                    [left, right],
                    node,
                )
                left = synthesize_tracer_call_ast(
                    NOT,
                    [inside],
                    node,
                )

        return left

    def visit_Slice(self, node: ast.Slice) -> ast.Call:
        slice_arguments = [self.visit(node.lower), self.visit(node.upper)]
        if node.step is not None:
            slice_arguments.append(self.visit(node.step))
        return synthesize_tracer_call_ast(
            slice.__name__,
            slice_arguments,
            node,
        )

    def visit_Subscript(self, node: ast.Subscript) -> ast.Call:
        args = [self.visit(node.value)]
        index = self._get_index(node)
        if (
            isinstance(index, ast.Name)
            or isinstance(index, ast.Constant)
            or isinstance(index, ast.List)
        ):
            args.append(self.visit(index))
        elif isinstance(index, ast.Slice):
            args.append(self.visit_Slice(index))
        else:
            raise NotImplementedError(
                "Subscript for multiple indices not supported."
            )
        if isinstance(node.ctx, ast.Load):
            return synthesize_tracer_call_ast(
                GET_ITEM,
                args,
                node,
            )
        elif isinstance(node.ctx, ast.Del):
            raise NotImplementedError(
                "Subscript with ctx=ast.Del() not supported."
            )
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
                        arg=FUNCTION_NAME,
                        value=ast.Constant(value=function_name),
                    ),
                    ast.keyword(
                        arg=SYNTAX_DICTIONARY,
                        value=syntax_dictionary,
                    ),
                ],
            ),
        )

    def visit_Attribute(self, node: ast.Attribute) -> ast.Call:

        return synthesize_tracer_call_ast(
            GETATTR,
            [self.visit(node.value), ast.Constant(value=node.attr)],
            node,
        )
