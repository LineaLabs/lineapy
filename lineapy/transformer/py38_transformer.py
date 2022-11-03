import ast

from lineapy.transformer.base_transformer import BaseTransformer


class Py38Transformer(BaseTransformer):
    def visit_Index(self, node: ast.Index) -> ast.AST:
        # ignoring types because these classes were entirely removed without backward support in 3.9
        return self.visit(node.value)  # type: ignore

    def visit_ExtSlice(self, node: ast.ExtSlice) -> ast.Tuple:
        # ignoring types because these classes were entirely removed without backward support in 3.9
        elem_nodes = [self.visit(elem) for elem in node.dims]  # type: ignore
        return ast.Tuple(
            elts=list(elem_nodes),
        )
