#
#
# type:ignore
import ast

import pytest
from mock import MagicMock

from lineapy.transformer.node_transformer import NodeTransformer


class TestNodeTransformer:
    nt: NodeTransformer

    @pytest.fixture(autouse=True)
    def before_everything(self):
        nt = NodeTransformer(
            "", MagicMock(), MagicMock()  # SourceCodeLocation(0, 0, 0, 0)
        )
        assert nt is not None
        self.nt = nt

    def test_lambda_executes_as_expression(self):
        self.nt._exec_expression = MagicMock()
        self.nt._exec_statement = MagicMock()

        # this inits an ast.Module containing one expression whose value is a ast.lambda
        test_node = ast.parse("lambda x: x + 10")
        lambda_node = test_node.body[0].value
        self.nt.generic_visit(lambda_node)
        self.nt._exec_statement.assert_not_called()
        self.nt._exec_expression.assert_called_once()

    def test_assign_executes(self):
        test_node = ast.parse("a = 10")
        self.nt.visit_Assign = MagicMock()
        self.nt.visit(test_node.body[0])
        self.nt.visit_Assign.assert_called_once_with(test_node.body[0])

    def test_assign_calls_tracer_assign(self):
        self.nt.get_source = MagicMock()
        test_node = ast.parse("a = 10")
        tracer = self.nt.tracer
        self.nt.visit(test_node.body[0])
        # self.nt.visit_Assign.assert_called_once_with(test_node.body[0])
        tracer.assign.assert_called_once_with(
            "a", self.nt.tracer.literal.return_value
        )
