#
#
# type:ignore
import ast

import pytest
from mock import MagicMock, patch

from lineapy.transformer.node_transformer import NodeTransformer, transform


@patch(
    "lineapy.transformer.node_transformer.NodeTransformer",
)
def test_transform_fn(nt_mock: MagicMock):
    """
    Test that the transform function calls the NodeTransformer
    """
    mocked_tracer = MagicMock()
    source_location = MagicMock()
    transform("x = 1", source_location, mocked_tracer)
    nt_mock.assert_called_once_with("x = 1", source_location, mocked_tracer)
    mocked_tracer.db.commit.assert_called_once()
    # TODO - test that source giver is called only for 3.7 and below


class TestNodeTransformer:
    nt: NodeTransformer

    basic_tests = (
        "code, visitor, call_count",
        [
            ("a[2:3]", "Slice", 2),
            ("a[2:3:2]", "Slice", 2),
            ("a[2:3]", "Subscript", 2),
            ("a.x", "Attribute", 1),
            ("{'a': 1}", "Dict", 1),
            ("a < b", "Compare", 1),
            ("a not in []", "Compare", 3),
            ("a + b", "BinOp", 1),
            ("a or b", "BoolOp", 1),
            ("[1,2]", "List", 1),
            # ("{1,2}", "Set", 1),
            # tuple eventually calls tracer.call but we've mocked out the whole thing
            ("(1,2)", "Tuple", 0),
            ("not True", "UnaryOp", 1),
            ("10", "Constant", 0),  # this will break with 3.7
            ("assert True", "Assert", 1),
            ("fn(*args)", "Expr", 1),
            ("fn(*args)", "Call", 1),
            ("fn(*args)", "Starred", 1),
            ("fn(*args)", "Name", 1),
        ],
    )
    # TODO pull out constant to handle 3.7 vs 3.9 etc
    # TODO handle visit_Name as its own test
    # TODO import, assert, module, starred
    basic_test_ids = [
        "slice",
        "slice_with_step",
        "subscript",
        "attribute",
        "dict",
        "compare",
        "compare_notin",
        "binop",
        "boolop",
        "list",
        # "set",
        "tuple",
        "unaryop",
        "constant",
        "assert",
        "expr",
        "call",
        "starred",
        "name",
    ]

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
        tracer.assign.assert_called_once_with("a", tracer.literal.return_value)

    @pytest.mark.parametrize(
        "code",
        ["a[3]=10", "a.x =10"],
        ids=["assign_subscript", "assign_attribute"],
    )
    def test_assign_subscript_attribute_calls_tracer_assign(self, code):
        self.nt.get_source = MagicMock()
        test_node = ast.parse(code)
        tracer = self.nt.tracer
        self.nt.visit(test_node.body[0])
        tracer.call.assert_called_once_with(
            tracer.lookup_node.return_value,
            self.nt.get_source.return_value,
            tracer.lookup_node.return_value,
            tracer.literal.return_value,
            tracer.literal.return_value,
        )

    def test_visit_delete_executes(self):
        test_node = ast.parse("del a")
        with pytest.raises(NotImplementedError):
            self.nt.visit_Delete(test_node.body[0])

        self.nt.visit_Delete = MagicMock()
        self.nt.visit(test_node.body[0])
        self.nt.visit_Delete.assert_called_once_with(test_node.body[0])

    @pytest.mark.parametrize(
        "code", ["del a[3]", "del a.x"], ids=["delitem", "delattr"]
    )
    def test_visit_delete_subscript_attribute_calls_tracer_call(self, code):
        self.nt.get_source = MagicMock()
        test_node = ast.parse(code)
        tracer = self.nt.tracer
        self.nt.visit(test_node.body[0])
        tracer.call.assert_called_once_with(
            tracer.lookup_node.return_value,
            self.nt.get_source.return_value,
            tracer.lookup_node.return_value,
            tracer.literal.return_value,
        )

    # catch all for any ast nodes that do not have if conditions and/or very little logic

    @pytest.mark.parametrize(*basic_tests, ids=basic_test_ids)
    def test_code_visited_calls_tracer_call(self, code, visitor, call_count):
        test_node = ast.parse(code)
        self.nt.visit(test_node)
        # doing this so that we can select which function in tracer gets called.
        # might be overkill though so leaving it at this
        tracer_fn = getattr(self.nt.tracer, "call")
        assert tracer_fn.call_count == call_count

    @pytest.mark.parametrize(*basic_tests, ids=basic_test_ids)
    def test_code_visits_right_visitor(self, code, visitor, call_count):
        test_node = ast.parse(code)
        self.nt.__setattr__("visit_" + visitor, MagicMock())
        nt_visitor = self.nt.__getattribute__("visit_" + visitor)
        self.nt.visit(test_node)
        nt_visitor.assert_called_once()
