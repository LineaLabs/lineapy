import ast
from lineapy.data.types import CallNode, Node
from typing import Union, cast, Any


from lineapy import linea_publish
from lineapy.constants import (
    DEL_ATTR,
    DEL_ITEM,
    ADD,
    SET_ATTR,
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
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.lineabuiltins import __build_list__
from lineapy.transformer.transformer_util import (
    create_lib_attributes,
    extract_concrete_syntax_from_node,
    tracer_call_with_syntax,
)
from lineapy.utils import (
    CaseNotHandledError,
    UserError,
    InvalidStateError,
    info_log,
)


class NodeTransformer(ast.NodeTransformer):
    """
    Notes:
    - Need to be careful about the order by which these calls are invoked
      so that the transformation do not get called more than once.
    """

    # TODO: Remove source
    def __init__(self, source: str, tracer: Tracer):
        self.source = source
        self.tracer = tracer

    def _get_code_from_node(self, node):
        return ast.get_source_segment(self.source, node)

    def visit(self, node: ast.AST) -> Any:
        try:
            return super().visit(node)
        except Exception as e:
            code_context = self._get_code_from_node(node)
            if code_context:
                info_log(
                    f"Error while transforming code: \n\n{code_context}\n"
                )
            raise e

    def visit_Import(self, node):
        """
        Similar to `visit_ImportFrom`, slightly different class syntax
        """
        # result = []
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        for lib in node.names:
            self.tracer.trace_import(
                lib.name,
                syntax_dictionary,
                alias=lib.asname,
            )

    def visit_ImportFrom(self, node):
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        self.tracer.trace_import(
            node.module,
            syntax_dictionary,
            attributes=create_lib_attributes(node.names),
        )

    def visit_Name(self, node: ast.Name) -> Node:
        return self.tracer.lookup_node(node.id)

    def visit_Call(self, node):
        """ """
        function_name, function_module = self.get_call_function_name(node)
        # a little hacky, assume no one else would have a function name
        #   called linea_publish
        if function_name == linea_publish.__name__:
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
                # description_node = cast(ast.Constant, node.args[1])
                return self.tracer.publish(var_node.id, node.args[1].value)
            else:
                return self.tracer.publish(var_node.id)
        else:  # this is the normal case, non-publish
            argument_nodes = [self.visit(arg) for arg in node.args]
            keyword_argument_nodes = [
                (arg.arg, self.visit(arg.value)) for arg in node.keywords
            ]
            # TODO: support keyword arguments as well
            return tracer_call_with_syntax(
                self.tracer,
                function_name,
                argument_nodes,
                node,
                function_module=function_module,
                keyword_arguments=keyword_argument_nodes,
            )

    def visit_Delete(self, node: ast.Delete):
        target = node.targets[0]

        if isinstance(target, ast.Name):
            raise NotImplementedError(
                "We do not support unassigning a variable"
            )
        elif isinstance(target, ast.Subscript):
            return tracer_call_with_syntax(
                self.tracer,
                DEL_ITEM,
                [self.visit(target.value), self.visit(target.slice)],
                node,
            )
        elif isinstance(target, ast.Attribute):
            return tracer_call_with_syntax(
                self.tracer,
                DEL_ATTR,
                [
                    self.visit(target.value),
                    self.visit(ast.Constant(value=target.attr)),
                ],
                node,
            )
        else:
            raise NotImplementedError(
                f"We do not support deleting {type(target)}"
            )

    def visit_Constant(self, node: ast.Constant):
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        return self.tracer.literal(node.value, syntax_dictionary)

    def visit_Assign(self, node: ast.Assign):
        """
        Assign currently special cases for:
        - Subscript, e.g., `ls[0] = 1`
        - Constant, e.g., `a = 1`
        - Call, e.g., `a = foo()`

        TODO
        - None variable assignment, should be turned into a setattr call
          not an assignment, so we might need to change the return signature
          from ast.Expr.
        """
        # TODO support multiple assignment
        assert len(node.targets) == 1

        syntax_dictionary = extract_concrete_syntax_from_node(node)
        if isinstance(node.targets[0], ast.Subscript):
            # Assigning a specific value to an index
            subscript_target: ast.Subscript = node.targets[0]
            index = subscript_target.slice
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
                return tracer_call_with_syntax(
                    self.tracer,
                    SET_ITEM,
                    argument_nodes,
                    node,
                )
                # return ast.Expr(value=call)

            raise NotImplementedError(
                "Assignment for Subscript supported only for Constant and Name"
                " indices."
            )
        # e.g. `x.y = 10`
        elif isinstance(node.targets[0], ast.Attribute):
            target = node.targets[0]
            return tracer_call_with_syntax(
                self.tracer,
                SET_ATTR,
                [
                    self.visit(target.value),
                    self.visit(ast.Constant(target.attr)),
                    self.visit(node.value),
                ],
                node,
            )
            # return ast.Expr(value=call)

        if not isinstance(node.targets[0], ast.Name):
            raise NotImplementedError(
                "Other assignment types are not supported"
            )
        variable_name = node.targets[0].id  # type: ignore

        self.tracer.assign(
            variable_name,
            self.visit(node.value),
            syntax_dictionary,
        )

    def visit_List(self, node: ast.List) -> CallNode:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return tracer_call_with_syntax(
            self.tracer, __build_list__.__name__, elem_nodes, node
        )

    def visit_BinOp(self, node: ast.BinOp) -> CallNode:
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
        op = ast_to_op_map[node.op.__class__]  # type: ignore
        argument_nodes = [self.visit(node.left), self.visit(node.right)]
        return tracer_call_with_syntax(
            self.tracer,
            op,
            argument_nodes,
            node,
        )

    def visit_Compare(self, node: ast.Compare) -> CallNode:
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
                left = tracer_call_with_syntax(
                    self.tracer,
                    ast_to_op_map[op.__class__],
                    [left, right],
                    node,
                )
            elif isinstance(op, ast.NotIn):
                # need to call operator.not_ on __contains___
                inside = tracer_call_with_syntax(
                    self.tracer,
                    ast_to_op_map[ast.In],
                    [left, right],
                    node,
                )
                left = tracer_call_with_syntax(
                    self.tracer,
                    NOT,
                    [inside],
                    node,
                )

        return left

    def visit_Slice(self, node: ast.Slice) -> CallNode:
        slice_arguments = [self.visit(node.lower), self.visit(node.upper)]
        if node.step is not None:
            slice_arguments.append(self.visit(node.step))
        return tracer_call_with_syntax(
            self.tracer,
            slice.__name__,
            slice_arguments,
            node,
        )

    def visit_Subscript(self, node: ast.Subscript) -> CallNode:
        args = [self.visit(node.value)]
        index = node.slice
        args.append(self.visit(index))
        if isinstance(node.ctx, ast.Load):
            return tracer_call_with_syntax(
                self.tracer,
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

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        For now, assume the function is pure, i.e.:
        - no globals
        - no writing to variables defined outside the scope
        TODO: remove these limitatsynthesize_tracer_call_astions in future PRs
        """
        # apparently FunctionDef is not inside Expr so for the new call we need to create new line
        function_name = node.name
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        self.tracer.define_function(function_name, syntax_dictionary)

    def visit_Attribute(self, node: ast.Attribute) -> CallNode:

        return tracer_call_with_syntax(
            self.tracer,
            GETATTR,
            [
                self.visit(node.value),
                self.visit(ast.Constant(value=node.attr)),
            ],
            node,
        )

    def get_call_function_name(
        self, node: ast.Call
    ) -> tuple[str, Union[Node, None, str]]:
        """
        Returns (function_name, function_module)
        """
        func = node.func
        if isinstance(func, ast.Name):
            return func.id, None
        if isinstance(func, ast.Attribute):
            value = func.value
            module: ast.expr
            if isinstance(value, ast.Name):
                module = value.id
            else:
                module = self.visit(value)
            return func.attr, module

        raise CaseNotHandledError("Other types of function calls!")
