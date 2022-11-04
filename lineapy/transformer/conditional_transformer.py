import ast

# import sys
from typing import Any

from lineapy.data.types import NodeType
from lineapy.transformer.base_transformer import BaseTransformer
from lineapy.utils.utils import get_new_id


class ConditionalTransformer(BaseTransformer):
    def visit_If(self, node: ast.If) -> Any:
        test_call_node = self.visit(node.test)

        node_id = get_new_id()
        else_id = get_new_id() if len(node.orelse) > 0 else None

        # We first check the value of the test node, depending on it's truth
        # value we might have two cases as described below
        if self.tracer.executor._id_to_value[test_call_node.id]:
            # In case the test condition is truthy, we will visit only the
            # statements within the body of the If node.
            with self.tracer.get_control_node(
                NodeType.IfNode,
                node_id,
                else_id,
                self.get_source(node.test),
                test_call_node.id,
                None,
            ):
                for stmt in node.body:
                    self.visit(stmt)
            # For the statements within the orelse of the IfNode, since they
            # are actually not executed, we simply treat all of the enclosed
            # statements as a black box, and get a literal node containing all
            # the unexecuted statements. We then create an ElseNode which
            # points to the LiteralNode containing the unexecuted statements,
            # which ensures all the unexecuted statements are always included
            # in the sliced program
            if else_id is not None:
                with self.tracer.get_control_node(
                    NodeType.ElseNode,
                    else_id,
                    node_id,
                    self.get_else_source(node),
                    None,
                    self.get_black_box_without_executing(node.orelse).id,
                ):
                    pass
        else:
            # In this case, the test condition is falsy, so we reverse the
            # analysis above: the statements in the body of the If node are not
            # visited, hence they are treated as a blackbox, while the
            # statements within the orelse branch are visited, and we call the
            # visit() method on these statements.
            with self.tracer.get_control_node(
                NodeType.IfNode,
                node_id,
                else_id,
                self.get_source(node.test),
                test_call_node.id,
                self.get_black_box_without_executing(node.body).id,
            ):
                pass
            if else_id is not None:
                with self.tracer.get_control_node(
                    NodeType.ElseNode,
                    else_id,
                    node_id,
                    self.get_else_source(node),
                ):
                    for stmt in node.orelse:
                        self.visit(stmt)
