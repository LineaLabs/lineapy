# Setting up for mypy to ignore this file
# This file uses mocks which have dynamically defined functions.
# this does not sit well with mypy who needs to know what functions a class has
# type:ignore
import ast
import sys

import asttokens
import pytest
from mock import MagicMock, patch

from lineapy.transformer.node_transformer import NodeTransformer, transform
from lineapy.transformer.source_giver import SourceGiver


def _get_ast_node(code):
    node = ast.parse(code)
    if sys.version_info < (3, 8):  # give me endlines!
        asttokens.ASTTokens(code, parse=False, tree=node)
        SourceGiver().transform(node)

    return node


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

    basic_tests_list = [
        ("a[2:3]", "Slice", 1, 2),
        ("a[2:3:2]", "Slice", 1, 2),
        ("a[2:3]", "Subscript", 1, 2),
        ("a.x", "Attribute", 1, 1),
        ("{'a': 1}", "Dict", 1, 1),
        ("a < b", "Compare", 1, 1),
        ("a not in []", "Compare", 1, 3),
        ("a + b", "BinOp", 1, 1),
        ("a or b", "BoolOp", 1, 1),
        ("[1,2]", "List", 1, 1),
        # set is xfailing right now
        # ("{1,2}", "Set", 1, 1),
        # tuple eventually calls tracer.call but we've mocked out the whole thing
        ("(1,2)", "Tuple", 1, 0),
        ("not True", "UnaryOp", 1, 1),
        ("assert True", "Assert", 1, 1),
        ("fn(*args)", "Expr", 1, 1),
        ("fn(*args)", "Call", 1, 1),
        # this reflects and update where we dont visit starred anymore
        ("fn(*args)", "Starred", 0, 1),
        ("fn(*args)", "Name", 1, 1),
        ("print(*'mystring')", "Starred", 0, 1),
        # calls tracer.trace_import but this list checks for tracer.call calls
        ("import math", "Import", 1, 0),
        # calls tracer.trace_import but this list checks for tracer.call calls
        # TODO - importfrom calls transform_utils which should really be mocked out and
        # tested on their own, in true spirit of unit testing
        ("from math import sqrt", "ImportFrom", 1, 0),
        ("a, b = (1,2)", "Assign", 1, 3),
        ("lambda x: x + 10", "Lambda", 1, 1),
    ]

    # TODO handle visit_Name as its own test
    # TODO module
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
        "assert",
        "expr",
        "call",
        "starred",
        "name",
        "starred_str",
        "import",
        "import_from",
        "assign_tuple",
        "lambda",
    ]

    if sys.version_info < (3, 8):
        basic_tests_list += (("10", "Num", 1, 0),)
        # extslice does not call tracer.call but it contains a slice node.
        # that along with subscript will result in two calls
        basic_tests_list += (("a[:,3]", "ExtSlice", 1, 2),)
        basic_test_ids += ["num"]
        basic_test_ids += ["extslice"]
    else:
        # this will break with 3.7
        basic_tests_list += (("10", "Constant", 1, 0),)
        basic_tests_list += (("a[:,3]", "Slice", 1, 2),)
        basic_test_ids += ["constant"]
        basic_test_ids += ["slice_with_ext"]

    basic_tests = (
        "code, visitor, visitor_count, call_count",
        basic_tests_list,
    )

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
        test_node = _get_ast_node("lambda x: x + 10")
        lambda_node = test_node.body[0].value
        self.nt.generic_visit(lambda_node)
        self.nt._exec_statement.assert_not_called()
        self.nt._exec_expression.assert_called_once()

    def test_assign_executes(self):
        test_node = _get_ast_node("a = 10")
        self.nt.visit_Assign = MagicMock()
        self.nt.visit(test_node.body[0])
        self.nt.visit_Assign.assert_called_once_with(test_node.body[0])

    def test_assign_calls_tracer_assign(self):
        self.nt.get_source = MagicMock()
        test_node = _get_ast_node("a = 10")
        tracer = self.nt.tracer
        self.nt.visit(test_node.body[0])
        tracer.assign.assert_called_once_with("a", tracer.literal.return_value)

    @pytest.mark.parametrize(
        "code",
        ["a[3]=10", "a.x =10"],
        ids=["assign_subscript", "assign_attribute"],
    )
    def test_assign_subscript_attribute_calls_tracer_assign(self, code):
        self.nt.get_source = MagicMock()
        test_node = _get_ast_node(code)
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
        test_node = _get_ast_node("del a")
        with pytest.raises(NotImplementedError):
            self.nt.visit_Delete(test_node.body[0])

        self.nt.visit_Delete = MagicMock()
        self.nt.visit(test_node.body[0])
        self.nt.visit_Delete.assert_called_once_with(test_node.body[0])

    def test_get_else_source_space_after_if_block(self):
        CODE = """if a:\n\tb\n\n\nelse:\n\tc"""
        test_node = _get_ast_node(CODE).body[0]
        source_location = self.nt.get_else_source(test_node)
        # Checking whether all cases to set end_lineno for returned
        # SourceLocation are hit
        assert test_node.orelse[0].lineno - 1 == source_location.end_lineno
        lines = slice(source_location.lineno, source_location.end_lineno + 1)
        # Ensuring that the line including "else:" in code above gets included
        assert 5 in range(lines.start, lines.stop)

    def test_get_else_source_no_newline_after_else_keyword(self):
        CODE = """if a:\n\tb\nelse: c"""
        test_node = _get_ast_node(CODE).body[0]
        source_location = self.nt.get_else_source(test_node)
        # Checking whether all cases to set end_lineno for returned
        # SourceLocation are hit
        assert test_node.body[-1].end_lineno + 1 == source_location.end_lineno
        lines = slice(source_location.lineno, source_location.end_lineno + 1)
        # Ensuring that the line including "else:" in code above gets included
        assert 3 in range(lines.start, lines.stop)

    @pytest.mark.parametrize(
        "code", ["del a[3]", "del a.x"], ids=["delitem", "delattr"]
    )
    def test_visit_delete_subscript_attribute_calls_tracer_call(self, code):
        self.nt.get_source = MagicMock()
        test_node = _get_ast_node(code)
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
    def test_code_visited_calls_tracer_call(
        self, code, visitor, visitor_count, call_count
    ):
        self.nt._get_code_from_node = MagicMock()
        test_node = _get_ast_node(code)
        self.nt.visit(test_node)
        # doing this so that we can select which function in tracer gets called.
        # might be overkill though so leaving it at this
        tracer_fn = getattr(self.nt.tracer, "call")
        assert tracer_fn.call_count == call_count

    @pytest.mark.parametrize(*basic_tests, ids=basic_test_ids)
    def test_code_visits_right_visitor(
        self, code, visitor, visitor_count, call_count
    ):
        test_node = _get_ast_node(code)
        self.nt.__setattr__("visit_" + visitor, MagicMock())
        nt_visitor = self.nt.__getattribute__("visit_" + visitor)
        self.nt.visit(test_node)
        nt_visitor.call_count == visitor_count
