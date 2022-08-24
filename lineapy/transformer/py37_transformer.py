import ast

# import sys
from typing import Optional

from lineapy.data.types import LiteralNode, Node, SourceCode, SourceLocation
from lineapy.instrumentation.tracer import Tracer


class Py37Transformer(ast.NodeTransformer):
    def __init__(
        self,
        source_code: SourceCode,
        tracer: Tracer,
    ):
        self.source_code = source_code
        self.tracer = tracer
        # The result of the last line, a node if it was an expression,
        # None if it was a statement. Used by ipython to grab the last value
        self.last_statement_result: Optional[Node] = None

    def generic_visit(self, node):
        """
        had to rewrite this because apparently if we process nodes in a list, it just extends it willy nilly
        """
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def visit_Ellipsis(self, node: ast.Ellipsis) -> LiteralNode:
        """
        Note
        ----

        Deprecated in Python 3.8
        """
        return self.tracer.literal(..., self.get_source(node))

    def visit_Str(self, node: ast.Str) -> LiteralNode:
        """
        Note
        ----

        Deprecated in Python 3.8
        """
        return self.tracer.literal(node.s, self.get_source(node))

    def visit_Num(self, node: ast.Num) -> LiteralNode:
        """
        Note
        ----

        Deprecated in Python 3.8
        """
        return self.tracer.literal(node.n, self.get_source(node))

    def visit_NameConstant(self, node: ast.NameConstant) -> LiteralNode:
        """
        Note
        ----

        Deprecated in Python 3.8
        """
        return self.tracer.literal(node.value, self.get_source(node))

    def visit_Bytes(self, node: ast.Bytes) -> LiteralNode:
        """
        Note
        ----

        Deprecated in Python 3.8
        """
        return self.tracer.literal(node.s, self.get_source(node))

    def get_source(self, node: ast.AST) -> Optional[SourceLocation]:
        if not hasattr(node, "lineno"):
            return None
        return SourceLocation(
            source_code=self.source_code,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=node.end_lineno,  # type: ignore
            end_col_offset=node.end_col_offset,  # type: ignore
        )
