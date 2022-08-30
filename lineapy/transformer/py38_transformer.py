import ast

from lineapy.data.types import Node
from lineapy.transformer.base_transformer import BaseTransformer


class Py38Transformer(BaseTransformer):
    def visit_Index(self, node: ast.Index) -> ast.AST:
        return node.value

    def visit_ExtSlice(self, node: ast.ExtSlice) -> Node:
        elem_nodes = [self.visit(elem) for elem in node.dims]
        return self.tracer.tuple(
            *elem_nodes,
            source_location=self.get_source(node),
        )
