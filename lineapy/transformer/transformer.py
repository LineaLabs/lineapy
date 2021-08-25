from lineapy.transformer.constants import LINEAPY_IMPORT_LIB_NAME, LINEAPY_TRACER_NAME
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.data.types import Node
from typing import Any, List, Optional
import ast
from astor import to_source
from lineapy.utils import info_log

from astpretty import pprint

# FIXME: find the typing for AST nodes
TreeNodeType = Any


class Transformer:
    """
    The reason why we have the transformer and the instrumentation separate is that we need runtime information when creating the nodes.
    If we created the instrumentation statically, then the node level information would be lost.
    """

    def __init__(self):
        self.has_initiated = False

    def transform(self, code: str, session_name: Optional[str], one_shot=True) -> str:
        info_log("transform", code)
        transformed_tree = self.transform_user_code(code)
        if one_shot:
            enter_tree = self.create_enter("script", session_name)
            exit_tree = self.create_exit()
            transformed_tree.body = enter_tree + transformed_tree.body + exit_tree

        # pprint(transformed_tree, show_offsets=False)
        transformed_code = to_source(transformed_tree)
        return transformed_code
        # return ""

    def transform_user_code(self, code: str) -> ast.Module:
        # FIXME: just a pass thru for now
        node_transformer = NodeTransformer(code)
        tree = ast.parse(code)
        new_tree = node_transformer.visit(tree)
        return new_tree

    def create_exit(self) -> List[TreeNodeType]:
        """
        Hack: just returning raw string for now... We can invest in nodes if there is a feature that requires such.
        note maybe we could move this to a standalone function
        """
        return [
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                        attr="exit",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            )
        ]

    def create_enter(
        self, environment_type: str, session_name: Optional[str]
    ) -> List[TreeNodeType]:
        """
        Also a hack for now...
        """
        import_node = ast.Import(
            names=[ast.alias(name=LINEAPY_IMPORT_LIB_NAME, asname=None)],
        )
        tracer_node = ast.Assign(
            id=LINEAPY_TRACER_NAME,
            ctx=ast.Store(),
            targets=[ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="lineapy", ctx=ast.Load()),
                    attr="Tracer",
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Constant(value=environment_type),
                    ast.Constant(value=session_name),
                ],
                keywords=[],
            ),
        )
        return [import_node, tracer_node]
