import ast
import lineapy
from lineapy.data.types import CallNode, Node
from typing import Optional, cast, Any


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
)
from lineapy.utils import (
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
        """
        Should return a Node when visiting expressions, to chain them,
        or a None when visiting statements.
        """
        try:
            return super().visit(node)
        except Exception as e:
            code_context = self._get_code_from_node(node)
            if code_context:
                info_log(
                    f"Error while transforming code: \n\n{code_context}\n"
                )
            raise e

    def visit_Import(self, node: ast.Import) -> None:
        """
        Similar to `visit_ImportFrom`, slightly different class syntax
        """
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        for lib in node.names:
            self.tracer.trace_import(
                lib.name,
                syntax_dictionary,
                alias=lib.asname,
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        assert node.module
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        self.tracer.trace_import(
            node.module,
            syntax_dictionary,
            attributes=create_lib_attributes(node.names),
        )

    def visit_Name(self, node: ast.Name) -> Node:
        return self.tracer.lookup_node(node.id)

    def visit_Call(self, node: ast.Call) -> Optional[CallNode]:
        """
        Returns None if visiting special publish linea publish, which cannot be chained
        """
        # function_name, function_module = self.get_call_function_name(node)

        # a little hacky, assume no one else would have a function name
        #   called linea_publish

        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            # TODO: Rename linea publish and possibly make more robust
            # to allow import from
            and node.func.attr == linea_publish.__name__
            and node.func.value.id == lineapy.__name__
        ):
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
                self.tracer.publish(var_node.id, node.args[1].value)
            else:
                self.tracer.publish(var_node.id)
            return None
        # this is the normal case, non-publish
        argument_nodes = [self.visit(arg) for arg in node.args]
        keyword_argument_nodes = {
            cast(str, arg.arg): self.visit(arg.value) for arg in node.keywords
        }
        function_node = self.visit(node.func)

        return self.tracer.call(
            function_node,
            extract_concrete_syntax_from_node(node),
            *argument_nodes,
            **keyword_argument_nodes,
        )

    def visit_Delete(self, node: ast.Delete) -> None:
        target = node.targets[0]

        syntax_dictionary = extract_concrete_syntax_from_node(node)
        if isinstance(target, ast.Name):
            raise NotImplementedError(
                "We do not support unassigning a variable"
            )
        elif isinstance(target, ast.Subscript):
            self.tracer.call(
                self.tracer.lookup_node(DEL_ITEM),
                syntax_dictionary,
                self.visit(target.value),
                self.visit(target.slice),
            )
        elif isinstance(target, ast.Attribute):
            self.tracer.call(
                self.tracer.lookup_node(DEL_ATTR),
                syntax_dictionary,
                self.visit(target.value),
                self.visit(ast.Constant(value=target.attr)),
            )
        else:
            raise NotImplementedError(
                f"We do not support deleting {type(target)}"
            )

    def visit_Constant(self, node: ast.Constant) -> Node:
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        return self.tracer.literal(node.value, syntax_dictionary)

    def visit_Assign(self, node: ast.Assign) -> None:
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

        # e.g., `x["y"] = 10`
        if isinstance(node.targets[0], ast.Subscript):
            subscript_target: ast.Subscript = node.targets[0]
            index = subscript_target.slice
            # note: isinstance(index, ast.List) only works for pandas,
            #  not Python lists
            # if isinstance(index, (ast.Constant, ast.Name, ast.List, ast.Slice)):
            self.tracer.call(
                self.tracer.lookup_node(SET_ITEM),
                syntax_dictionary,
                self.visit(subscript_target.value),
                self.visit(index),
                self.visit(node.value),
            )
            return None

        # e.g. `x.y = 10`
        elif isinstance(node.targets[0], ast.Attribute):
            target = node.targets[0]
            self.tracer.call(
                self.tracer.lookup_node(SET_ATTR),
                syntax_dictionary,
                self.visit(target.value),
                self.visit(ast.Constant(target.attr)),
                self.visit(node.value),
            )
            return None

        # FIXME: not sure what else is there...
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
        return None

    def visit_List(self, node: ast.List) -> CallNode:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        return self.tracer.call(
            self.tracer.lookup_node(__build_list__.__name__),
            syntax_dictionary,
            *elem_nodes,
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
        return self.tracer.call(
            self.tracer.lookup_node(op),
            extract_concrete_syntax_from_node(node),
            *argument_nodes,
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
                    extract_concrete_syntax_from_node(node),
                    left,
                    right,
                )
            elif isinstance(op, ast.NotIn):
                # need to call operator.not_ on __contains___
                inside = self.tracer.call(
                    self.tracer.lookup_node(ast_to_op_map[ast.In]),
                    extract_concrete_syntax_from_node(node),
                    left,
                    right,
                )
                left = self.tracer.call(
                    self.tracer.lookup_node(NOT),
                    extract_concrete_syntax_from_node(node),
                    inside,
                )

        return left

    def visit_Slice(self, node: ast.Slice) -> CallNode:
        assert node.lower and node.upper
        slice_arguments = [self.visit(node.lower), self.visit(node.upper)]
        if node.step is not None:
            slice_arguments.append(self.visit(node.step))
        return self.tracer.call(
            self.tracer.lookup_node(slice.__name__),
            extract_concrete_syntax_from_node(node),
            *slice_arguments,
        )

    def visit_Subscript(self, node: ast.Subscript) -> CallNode:
        args = [self.visit(node.value)]
        index = node.slice
        args.append(self.visit(index))
        if isinstance(node.ctx, ast.Load):
            return self.tracer.call(
                self.tracer.lookup_node(GET_ITEM),
                extract_concrete_syntax_from_node(node),
                *args,
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        For now, assume the function is pure, i.e.:
        - no globals
        - no writing to variables defined outside the scope
        """

        function_name = node.name
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        self.tracer.define_function(function_name, syntax_dictionary)

    def visit_Attribute(self, node: ast.Attribute) -> CallNode:

        return self.tracer.call(
            self.tracer.lookup_node(GETATTR),
            extract_concrete_syntax_from_node(node),
            self.visit(node.value),
            self.visit(ast.Constant(value=node.attr)),
        )
