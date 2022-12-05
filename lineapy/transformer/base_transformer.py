import ast
import sys
from typing import List, Optional

from lineapy.data.types import LiteralNode, Node, SourceCode, SourceLocation
from lineapy.instrumentation.tracer import Tracer


class BaseTransformer(ast.NodeTransformer):
    """
    .. note::

        - Need to be careful about the order by which these calls are invoked
          so that the transformation do not get called more than once.

    """

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

    def _get_code_from_node(self, node: ast.AST) -> Optional[str]:
        if sys.version_info < (3, 8):
            from lineapy.utils.deprecation_utils import get_source_segment

            return get_source_segment(self.source_code.code, node, padded=True)
        else:
            return ast.get_source_segment(
                self.source_code.code, node, padded=True
            )

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

    def get_else_source(self, node: ast.If) -> Optional[SourceLocation]:
        body_source = self.get_source(node.body[-1])
        orelse_source = (
            self.get_source(node.orelse[0]) if node.orelse else None
        )
        assert body_source, "Body of If/Else must have at least one statement"
        if not orelse_source:
            # If there is no else block, the else keyword would not be present
            return None
        return SourceLocation(
            source_code=self.source_code,
            # Else node can only start one line after if block, hence we add 1
            lineno=body_source.end_lineno + 1,
            col_offset=0,
            # Keyword else can be in the previous line or the same line as the
            # first statement of the else block
            end_lineno=max(
                orelse_source.lineno - 1, body_source.end_lineno + 1
            ),
            end_col_offset=orelse_source.col_offset,
        )

    def get_black_box_without_executing(
        self, nodes: List[ast.stmt]
    ) -> LiteralNode:
        # We simply create a LiteralNode with the code within the block
        # Processing a LiteralNode does not actually execute the statement
        assert (
            len(nodes) > 0
        ), "The code block should contain at least one statement."
        code = "\n".join(
            [
                str(self._get_code_from_node(node))
                for node in nodes
                if (self._get_code_from_node(node) is not None)
            ]
        )
        source_location = SourceLocation(
            source_code=self.source_code,
            lineno=nodes[0].lineno,
            col_offset=nodes[0].col_offset,
            end_lineno=nodes[-1].end_lineno,  # type: ignore
            end_col_offset=nodes[-1].end_col_offset,  # type: ignore
        )
        return self.tracer.literal(code, source_location=source_location)
