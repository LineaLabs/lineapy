import ast

from lineapy.transformer.base_transformer import BaseTransformer
from lineapy.utils.deprecation_utils import Constant


class Py37Transformer(BaseTransformer):
    def convert_to_constant(self, value, node) -> Constant:
        if not hasattr(
            node, "end_lineno"
        ):  # somehow didnt go through our sourcegiver
            return Constant(
                value=value, lineno=node.lineno, col_offset=node.col_offset
            )
        else:
            return Constant(
                value=value,
                lineno=node.lineno,
                end_lineno=node.end_lineno,  # type: ignore
                col_offset=node.col_offset,
                end_col_offset=node.end_col_offset,  # type: ignore
            )

    def visit_Ellipsis(self, node: ast.Ellipsis) -> Constant:
        return self.convert_to_constant(..., node)

    def visit_Str(self, node: ast.Str) -> Constant:
        return self.convert_to_constant(node.s, node)

    def visit_Num(self, node: ast.Num) -> Constant:
        return self.convert_to_constant(node.n, node)

    def visit_NameConstant(self, node: ast.NameConstant) -> Constant:
        return self.convert_to_constant(node.value, node)

    def visit_Bytes(self, node: ast.Bytes) -> Constant:
        return self.convert_to_constant(node.s, node)
