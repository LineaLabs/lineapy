import ast
from lineapy.transformer.analyze_scope import analyze_code_scope
import lineapy
from lineapy.data.types import CallNode, Node
from typing import Optional, Union, cast, Any


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
    POS,
    NEG,
    INVERT,
)
from lineapy.instrumentation.tracer import SyntaxDictionary, Tracer
from lineapy.lineabuiltins import (
    __build_list__,
    __assert__,
    __build_tuple__,
    __build_dict__,
    __build_dict_kwargs_sentinel__,
)
from lineapy.transformer.transformer_util import (
    create_lib_attributes,
    extract_concrete_syntax_from_node,
)
from lineapy.utils import (
    InternalLogicError,
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
                info_log(f"Error while transforming code: \n\n{code_context}\n")
            raise e

    def generic_visit(self, node: ast.AST) -> ast.AST:
        raise NotImplementedError(
            f"Don't know how to transform {type(node).__name__}"
        )

    def visit_Module(self, node: ast.Module) -> Any:
        return super().generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> Any:
        return super().generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        syntax_dictionary = extract_concrete_syntax_from_node(node)

        args = [self.visit(node.test)]
        if node.msg:
            args.append(self.visit(node.msg))
        self.tracer.call(
            self.tracer.lookup_node(__assert__.__name__),
            syntax_dictionary,
            *args,
        )

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
        TODO
        - None variable assignment, should be turned into a setattr call
          not an assignment, so we might need to change the return signature
          from ast.Expr.
        """
        assert len(node.targets) == 1
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        target = node.targets[0]
        self.visit_assign_value(
            target, self.visit(node.value), syntax_dictionary
        )

    def visit_assign_value(
        self,
        target: ast.AST,
        value_node: Node,
        syntax_dictionary: SyntaxDictionary,
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
                syntax_dictionary,
                self.visit(target.value),
                self.visit(index),
                value_node,
            )
        # e.g. `x.y = 10`
        elif isinstance(target, ast.Attribute):
            self.tracer.call(
                self.tracer.lookup_node(SET_ATTR),
                syntax_dictionary,
                self.visit(target.value),
                self.visit(ast.Constant(target.attr)),
                value_node,
            )
        elif isinstance(target, ast.Tuple):
            # Assigning to a tuple of values, is like indexing the value
            # and then assigning to each.
            # Technically, its unpacking the sequence and setting it to each,
            # but for now we just index and hope that all values we are assigning
            # to multiple values can be indexed.
            for i, target_el in enumerate(target.elts):
                self.visit_assign_value(
                    target_el,
                    self.tracer.call(
                        self.tracer.lookup_node(GET_ITEM),
                        {},
                        value_node,
                        self.tracer.literal(i, {}),
                    ),
                    {},
                )
        elif isinstance(target, ast.Name):
            variable_name = target.id
            self.tracer.assign(
                variable_name,
                value_node,
                syntax_dictionary,
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
        syntax_dictionary = extract_concrete_syntax_from_node(node)

        return self.tracer.call(
            self.tracer.lookup_node(ast_to_op_map[type(op)]),
            syntax_dictionary,
            self.visit(node.operand),
        )

    def visit_List(self, node: ast.List) -> CallNode:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        return self.tracer.call(
            self.tracer.lookup_node(__build_list__.__name__),
            syntax_dictionary,
            *elem_nodes,
        )

    def visit_Tuple(self, node: ast.Tuple) -> CallNode:
        elem_nodes = [self.visit(elem) for elem in node.elts]
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        return self.tracer.tuple(
            *elem_nodes, syntax_dictionary=syntax_dictionary
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
        stop_node = self.visit(node.upper) if node.upper else self.tracer.none()
        # From https://docs.python.org/3/library/functions.html?highlight=slice#slice
        # slice can be called in two ways:
        # 1. slice(stop) when the start and step are None
        if node.lower is None and node.step is None:
            args = [stop_node]
        # 2. slice(start, stop, [step]) otherwise
        else:
            start_node = (
                self.visit(node.lower) if node.lower else self.tracer.none()
            )
            args = [start_node, stop_node]
            if node.step:
                step_node = self.visit(node.step)
                args.append(step_node)

        return self.tracer.call(
            self.tracer.lookup_node(slice.__name__),
            extract_concrete_syntax_from_node(node),
            *args,
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

    def visit_Attribute(self, node: ast.Attribute) -> CallNode:

        return self.tracer.call(
            self.tracer.lookup_node(GETATTR),
            extract_concrete_syntax_from_node(node),
            self.visit(node.value),
            self.visit(ast.Constant(value=node.attr)),
        )

    def _visit_black_box(
        self,
        node: Union[
            ast.ListComp,
            ast.If,
            ast.For,
            ast.FunctionDef,
        ],
    ):
        syntax_dictionary = extract_concrete_syntax_from_node(node)
        code = self._get_code_from_node(node)
        if code is not None:
            scope = analyze_code_scope(code)
            input_values = {v: self.tracer.lookup_node(v) for v in scope.loaded}
            if code is None:
                raise InternalLogicError("Code block should not be empty")

            return self.tracer.exec(
                code=code,
                is_expression=isinstance(node, ast.ListComp),
                syntax_dictionary=syntax_dictionary,
                input_values=input_values,
                output_variables=list(scope.stored),
            )
        raise InternalLogicError(f"Cannod find code for node {node}")

    def visit_ListComp(self, node: ast.ListComp) -> Node:
        return self._visit_black_box(node)  # type: ignore

    def visit_If(self, node: ast.If) -> None:
        return self._visit_black_box(node)  # type: ignore

    def visit_For(self, node: ast.For) -> None:
        return self._visit_black_box(node)  # type: ignore

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        For now, assume the function is pure, i.e.:
        - no globals
        - no writing to variables defined outside the scope
        """

        return self._visit_black_box(node)  # type: ignore

    def visit_Dict(self, node: ast.Dict) -> CallNode:
        keys = node.keys
        values = node.values
        # Build a dict call from a list of tuples of each key, mapping to each value
        # If the key is None, use a sentinel value
        return self.tracer.call(
            self.tracer.lookup_node(__build_dict__.__name__),
            extract_concrete_syntax_from_node(node),
            *(
                self.tracer.tuple(
                    self.visit(k)
                    if k is not None
                    else self.tracer.call(
                        self.tracer.lookup_node(
                            __build_dict_kwargs_sentinel__.__name__
                        ),
                        {},
                    ),
                    self.visit(v),
                )
                for k, v in zip(keys, values)
            ),
        )
