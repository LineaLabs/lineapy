import ast

from lineapy.data.types import LiteralNode
from lineapy.transformer.base_transformer import BaseTransformer


class Py37Transformer(BaseTransformer):
    def visit_Ellipsis(self, node: ast.Ellipsis) -> LiteralNode:
        return self.tracer.literal(..., self.get_source(node))

    def visit_Str(self, node: ast.Str) -> LiteralNode:
        return self.tracer.literal(node.s, self.get_source(node))

    def visit_Num(self, node: ast.Num) -> LiteralNode:
        return self.tracer.literal(node.n, self.get_source(node))

    def visit_NameConstant(self, node: ast.NameConstant) -> LiteralNode:
        return self.tracer.literal(node.value, self.get_source(node))

    def visit_Bytes(self, node: ast.Bytes) -> LiteralNode:
        return self.tracer.literal(node.s, self.get_source(node))
