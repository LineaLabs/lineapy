import ast
import logging
import sys
from typing import Any, Optional, Union, cast

from lineapy.data.types import CallNode, Node, SourceLocation
from lineapy.transformer.base_transformer import BaseTransformer
from lineapy.transformer.transformer_util import create_lib_attributes
from lineapy.utils.constants import (
    ADD,
    BITAND,
    BITOR,
    BITXOR,
    DEL_ATTR,
    DEL_ITEM,
    DIV,
    EQ,
    FLOORDIV,
    GET_ITEM,
    GETATTR,
    GT,
    GTE,
    IN,
    INVERT,
    IS,
    ISNOT,
    LSHIFT,
    LT,
    LTE,
    MATMUL,
    MOD,
    MULT,
    NEG,
    NOT,
    NOTEQ,
    POS,
    POW,
    RSHIFT,
    SET_ATTR,
    SET_ITEM,
    SUB,
)
from lineapy.utils.deprecation_utils import Constant
from lineapy.utils.lineabuiltins import (
    l_alias,
    l_assert,
    l_dict,
    l_dict_kwargs_sentinel,
    l_exec_expr,
    l_exec_statement,
    l_list,
    l_unpack_ex,
    l_unpack_sequence,
)

logger = logging.getLogger(__name__)


class NodeTransformer(BaseTransformer):
    """
    .. note::

        - Need to be careful about the order by which these calls are invoked
          so that the transformation do not get called more than once.

    """

    def generic_visit(self, node: ast.AST):
        """
        This will capture any generic blackboxes. Now that we have a clean scope
        handling, we can separate them out into two types: expressions that return
        something and statements that return nothing
        """

        if isinstance(
            node,
            ast.stmt,
        ):
            if (
                isinstance(
                    node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
                )
                and len(node.decorator_list) > 0
            ):
                min_decorator_line = min(
                    [decorator.lineno for decorator in node.decorator_list]
                )
                # this might not be needed but adding in case older python has weirdness
                if min_decorator_line is not None:
                    node.lineno = min(min_decorator_line, node.lineno)
            return self._exec_statement(node)
        elif isinstance(node, ast.expr):
            return self._exec_expression(node)

    def visit_Module(self, node: ast.Module) -> Any:
        for stmt in node.body:
            self.last_statement_result = self.visit(stmt)

    def visit_Expr(self, node: ast.Expr) -> Node:
        value_node = node.value
        value_node.lineno = min(node.lineno, value_node.lineno)
        value_node.end_lineno = max(  # type:ignore
            node.end_lineno, value_node.end_lineno
        )
        return self.visit(value_node)

    def visit_Assert(self, node: ast.Assert) -> None:

        args = [self.visit(node.test)]
        if node.msg:
            args.append(self.visit(node.msg))
        self.tracer.call(
            self.tracer.lookup_node(l_assert.__name__),
            self.get_source(node),
            *args,
        )

    def visit_Import(self, node: ast.Import) -> None:
        """
        Similar to `visit_ImportFrom`, slightly different class syntax
        """
        for lib in node.names:
            self.tracer.trace_import(
                lib.name,
                self.get_source(node),
                alias=lib.asname,
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        assert node.module
        self.tracer.trace_import(
            node.module,
            self.get_source(node),
            attributes=create_lib_attributes(node.names),
        )

    def visit_Name(self, node: ast.Name) -> Node:
        return self.tracer.lookup_node(node.id, self.get_source(node))

    def visit_Call(self, node: ast.Call) -> Optional[CallNode]:
        """
        Returns None if visiting special publish linea publish,
          which cannot be chained
        """

        # this is the normal case, non-publish
        argument_nodes = []
        for arg in node.args:
            # special case for starred, we need to indicate that unpacking is required
            if isinstance(arg, ast.Starred):
                argument_nodes.append((True, self.visit(arg.value)))
            else:
                argument_nodes.append(self.visit(arg))
        keyword_argument_nodes = {
            (
                cast(str, arg.arg) if arg.arg is not None else f"unpack_{i}"
            ): self.visit(arg.value)
            for i, arg in enumerate(node.keywords)
        }
        function_node = self.visit(node.func)

        return self.tracer.call(
            function_node,
            self.get_source(node),
            *argument_nodes,
            **keyword_argument_nodes,
        )

    def visit_Delete(self, node: ast.Delete) -> None:
        target = node.targets[0]

        if isinstance(target, ast.Name):
            raise NotImplementedError(
                "We do not support un-assigning a variable"
            )
        elif isinstance(target, ast.Subscript):
            self.tracer.call(
                self.tracer.lookup_node(DEL_ITEM),
                self.get_source(node),
                self.visit(target.value),
                self.visit(target.slice),
            )
        elif isinstance(target, ast.Attribute):
            self.tracer.call(
                self.tracer.lookup_node(DEL_ATTR),
                self.get_source(node),
                self.visit(target.value),
                self.visit(ast.Constant(value=target.attr)),
            )
        else:
            raise NotImplementedError(
                f"We do not support deleting {type(target)}"
            )

    def visit_Constant(self, node: Union[ast.Constant, Constant]) -> Node:
        return self.tracer.literal(
            node.value,
            self.get_source(node),
        )

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        TODO
        ----
        - None variable assignment, should be turned into a setattr call
          not an assignment, so we might need to change the return signature
          from ast.Expr.
        """
        # target assignments are handled from left to right in Python
        # x = y = z -> x = z, y = z
        for target in node.targets:
            # handle special case of assigning aliases e.g. x = y
            if isinstance(target, ast.Name) and isinstance(
                node.value, ast.Name
            ):
                new_node = self.tracer.call(
                    self.tracer.lookup_node(l_alias.__name__),
                    self.get_source(node),
                    self.visit(node.value),
                )
                self.tracer.assign(
                    target.id,
                    new_node,
                )
            else:
                value_node = node.value
                value_node.lineno = min(node.lineno, value_node.lineno)
                # ignoring type because end_lineno will always be there for lineapy
                value_node.end_lineno = max(  # type:ignore
                    node.end_lineno, value_node.end_lineno  # type: ignore
                )

                self.visit_assign_value(
                    target,
                    self.visit(value_node),
                    self.get_source(node),
                )

    def visit_assign_value(
        self,
        target: ast.AST,
        value_node: Node,
        source_location: Optional[SourceLocation] = None,
    ) -> None:
        """
        Visits assigning a target node to a value. This is extracted out of
        visit_assign, so we can call it multiple times and pass in the value as a node,
        instead of as AST, when we are assigning to a tuple.
        Assign currently special cases for:
        - Subscript, e.g., `ls[0] = 1`
        - Constant, e.g., `a = 1`
        - Call, e.g., `a = foo()`
        """
        if isinstance(target, ast.Subscript):
            index = target.slice
            # note: isinstance(index, ast.List) only works for pandas,
            #  not Python lists
            # if isinstance(index, (ast.Constant, ast.Name, ast.List, ast.Slice)):
            self.tracer.call(
                self.tracer.lookup_node(SET_ITEM),
                source_location,
                self.visit(target.value),
                self.visit(index),
                value_node,
            )
        # e.g. `x.y = 10`
        elif isinstance(target, ast.Attribute):
            self.tracer.call(
                self.tracer.lookup_node(SET_ATTR),
                source_location,
                self.visit(target.value),
                self.visit(ast.Constant(target.attr)),
                value_node,
            )
        elif isinstance(target, ast.List) or isinstance(target, ast.Tuple):
            # Assigning to a tuple or list of values, is like indexing the value
            # and then assigning to each.
            if any(
                isinstance(target_el, ast.Starred) for target_el in target.elts
            ):
                # count number of elements before and after the Starred item
                before = 0
                for target_el in target.elts:
                    if isinstance(target_el, ast.Starred):
                        break
                    else:
                        before += 1
                after = len(target.elts) - before - 1
                # get a proper unpacked list of CallNode
                unpacked_nodes = self.tracer.call(
                    self.tracer.lookup_node(l_unpack_ex.__name__),
                    source_location,
                    value_node,
                    self.tracer.literal(before),
                    self.tracer.literal(after),
                )
            else:
                # get a proper unpacked list of CallNode
                unpacked_nodes = self.tracer.call(
                    self.tracer.lookup_node(l_unpack_sequence.__name__),
                    source_location,
                    value_node,
                    self.tracer.literal(len(target.elts)),
                )
            # visit all elements of the new list
            for i, target_el in enumerate(target.elts):
                if isinstance(target_el, ast.Starred):
                    target_el = target_el.value
                self.visit_assign_value(
                    target_el,
                    self.tracer.call(
                        self.tracer.lookup_node(GET_ITEM),
                        source_location,
                        unpacked_nodes,
                        self.tracer.literal(i),
                    ),
                    source_location,
                )
        elif isinstance(target, ast.Name):
            variable_name = target.id
            self.tracer.assign(
                variable_name,
                value_node,
            )
        else:
            raise NotImplementedError(
                "Other assignment types are not supported"
            )

        return None

    def visit_UnaryOp(self, node: ast.UnaryOp) -> CallNode:
        ast_to_op_map = {
            ast.Invert: INVERT,
            ast.Not: NOT,
            ast.UAdd: POS,
            ast.USub: NEG,
        }
        op = node.op

        return self.tracer.call(
            self.tracer.lookup_node(ast_to_op_map[type(op)]),
            self.get_source(node),
            self.visit(node.operand),
        )

    def visit_List(self, node: ast.List) -> CallNode:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return self.tracer.call(
            self.tracer.lookup_node(l_list.__name__),
            self.get_source(node),
            *elem_nodes,
        )

    def visit_Tuple(self, node: ast.Tuple) -> CallNode:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        return self.tracer.tuple(
            *elem_nodes,
            source_location=self.get_source(node),
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
        op = ast_to_op_map[node.op.__class__]
        argument_nodes = [self.visit(node.left), self.visit(node.right)]
        return self.tracer.call(
            self.tracer.lookup_node(op),
            self.get_source(node),
            *argument_nodes,
        )

    def visit_BoolOp(self, node: ast.BoolOp) -> CallNode:
        ast_to_op_map = {
            ast.Or: BITOR,
            ast.And: BITAND,
        }
        op = ast_to_op_map[node.op.__class__]
        value_nodes = [self.visit(value) for value in node.values]
        return self.tracer.call(
            self.tracer.lookup_node(op),
            self.get_source(node),
            *value_nodes,
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

        # TODO: either add more comments or refactor, hard to understand
        # ast.Compare can have an arbitrary number of operators
        # e.g., a < b <= c
        left = self.visit(node.left)
        for i in range(len(node.ops)):
            op = node.ops[i]
            right = self.visit(node.comparators[i])
            if isinstance(op, ast.In) or isinstance(op, ast.NotIn):
                # flip left and right since in(a, b) = b.contains(a)
                left, right = right, deepcopy(left)
            if op.__class__ in ast_to_op_map:
                left = self.tracer.call(
                    self.tracer.lookup_node(ast_to_op_map[op.__class__]),
                    self.get_source(node),
                    left,
                    right,
                )
            elif isinstance(op, ast.NotIn):
                # need to call operator.not_ on __contains___
                inside = self.tracer.call(
                    self.tracer.lookup_node(ast_to_op_map[ast.In]),
                    self.get_source(node),
                    left,
                    right,
                )
                left = self.tracer.call(
                    self.tracer.lookup_node(NOT),
                    self.get_source(node),
                    inside,
                )

        return left

    def visit_Slice(self, node: ast.Slice) -> CallNode:
        stop_node = (
            self.visit(node.upper) if node.upper else self.tracer.literal(None)
        )
        # From https://docs.python.org/3/library/functions.html?highlight=slice#slice
        # slice can be called in two ways:
        # 1. slice(stop) when the start and step are None
        if node.lower is None and node.step is None:
            args = [stop_node]
        # 2. slice(start, stop, [step]) otherwise
        else:
            start_node = (
                self.visit(node.lower)
                if node.lower
                else self.tracer.literal(None)
            )
            args = [start_node, stop_node]
            if node.step:
                step_node = self.visit(node.step)
                args.append(step_node)

        return self.tracer.call(
            self.tracer.lookup_node(slice.__name__),
            self.get_source(node),
            *args,
        )

    def visit_Subscript(self, node: ast.Subscript) -> CallNode:
        args = [self.visit(node.value)]
        index = node.slice
        args.append(self.visit(index))
        return self.tracer.call(
            self.tracer.lookup_node(GET_ITEM),
            self.get_source(node),
            *args,
        )

    def visit_Attribute(self, node: ast.Attribute) -> CallNode:

        return self.tracer.call(
            self.tracer.lookup_node(GETATTR),
            self.get_source(node),
            self.visit(node.value),
            self.visit(ast.Constant(value=node.attr)),
        )

    if sys.version_info >= (3, 8):

        def visit_NamedExpr(self, node: ast.NamedExpr) -> Any:
            # This is for expressions of the form (var := val), which behaves like an Assign statement
            # but also returns val so that it can be used for further assignments, comparisions etc.
            # without having to rewrite the expression.
            # For example: "if (x := 10) > 9:", which assigns 10 to x and checks 10 > 9.
            # We treat it similar to an Assign statement, with the difference that the assigned value
            # is also returned so that it can be re-used.

            if isinstance(node.target, ast.Name):
                new_node = self.tracer.call(
                    self.tracer.lookup_node(l_alias.__name__),
                    self.get_source(node),
                    self.visit(node.value),
                )
                self.tracer.assign(
                    node.target.id,
                    new_node,
                )
                return new_node
            else:
                raise NotImplementedError(
                    "Assignment using the walrus operator (:=) is only supported for identifiers"
                )

    def _exec_statement(self, node: ast.AST) -> None:
        code = self._get_code_from_node(node)
        assert code
        self.tracer.call(
            self.tracer.lookup_node(l_exec_statement.__name__),
            self.get_source(node),
            self.tracer.literal(code),
        )

    def _exec_expression(self, node: ast.AST) -> Node:
        code = self._get_code_from_node(node)
        assert code
        return self.tracer.call(
            self.tracer.lookup_node(l_exec_expr.__name__),
            self.get_source(node),
            self.tracer.literal(code),
        )

    def visit_Dict(self, node: ast.Dict) -> CallNode:
        keys = node.keys
        values = node.values
        # Build a dict call from a list of tuples of each key, mapping to each value
        # If the key is None, use a sentinel value
        return self.tracer.call(
            self.tracer.lookup_node(l_dict.__name__),
            self.get_source(node),
            *(
                self.tracer.tuple(
                    self.visit(k)
                    if k is not None
                    else self.tracer.call(
                        self.tracer.lookup_node(
                            l_dict_kwargs_sentinel.__name__
                        ),
                        None,
                    ),
                    self.visit(v),
                )
                for k, v in zip(keys, values)
            ),
        )
