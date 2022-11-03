import ast

from lineapy.transformer.base_transformer import BaseTransformer


class Py38Transformer(BaseTransformer):
    def visit_Index(self, node: ast.Index) -> ast.AST:
        return self.visit(node.value)

    def visit_ExtSlice(self, node: ast.ExtSlice) -> ast.Tuple:
        elem_nodes = [self.visit(elem) for elem in node.dims]
        return ast.Tuple(
            elts=list(elem_nodes),
        )
