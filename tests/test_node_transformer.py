import ast
from lineapy.data.types import SessionType
import astor

from lineapy.constants import (
    GET_ITEM,
    ADD,
    SUB,
    MULT,
    DIV,
    FLOORDIV,
    MOD,
    POW,
    LSHIFT,
    RSHIFT,
    BITOR,
    BITXOR,
    BITAND,
    MATMUL,
    EQ,
    NOTEQ,
    LT,
    LTE,
    GT,
    GTE,
    IS,
    NOT,
    ISNOT,
    IN,
    GET_ITEM,
    SET_ITEM,
)
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.utils import internal_warning_log
from tests.stub_data.graph_with_import import import_code
from tests.util import compare_ast


class TestNodeTransformer:
    # we might need some setup in the future, but for this one we are fine
    def test_compare_ast(self):
        code1 = "import math\na = 1"
        code2 = "import math\na =    1"
        code3 = "import math\na = 1"
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        tree3 = ast.parse(code3)
        assert compare_ast(tree1, tree2)
        assert compare_ast(tree1, tree3)

    @staticmethod
    def _check_equality(original_code: str, expected_transformed: str):
        node_transformer = NodeTransformer(original_code)
        tree = ast.parse(original_code)
        new_tree = node_transformer.visit(tree)
        expected_tree = ast.parse(expected_transformed)
        if not compare_ast(new_tree, expected_tree):
            internal_warning_log("Original code:\t" + original_code)
            internal_warning_log(
                "Transformed code:\t", astor.to_source(new_tree)
            )
            internal_warning_log(
                "Expected code:\t", astor.to_source(expected_tree)
            )
            assert False

    def test_visit_import(self, execute):
        simple_import = "import pandas"
        execute(simple_import)

        alias_import = "import pandas as pd"
        execute(alias_import)

    def test_visit_importfrom(self, execute):
        execute("from math import pow as power")

    def test_visit_call(self, execute):
        simple_call = "foo()"
        execute(simple_call, session_type=SessionType.STATIC)

        call_with_args = "foo(1, 2)"
        execute(call_with_args, session_type=SessionType.STATIC)

    def test_visit_call_kwargs(self, execute):
        call_with_keyword_args = "foo(b=1)"
        execute(call_with_keyword_args, session_type=SessionType.STATIC)

    def test_visit_assign(self, execute):
        simple_assign = "a = 1"
        execute(simple_assign)

        # TODO: Move to execute when #155 is done
        assign_variable = "a = foo"
        expected_assign_variable = (
            "lineapy_tracer.assign(variable_name='a',"
            " value_node=Variable('foo'),"
            "syntax_dictionary={'lineno':1,'col_offset':0,"
            "'end_lineno':1,'end_col_offset':7})"
        )
        self._check_equality(assign_variable, expected_assign_variable)

    def test_visit_list(self, execute):
        simple_list = "[1, 2]"
        execute(simple_list)

        variable_list = "[1, a]"
        execute(
            variable_list,
            session_type=SessionType.STATIC,
            exec_transformed_xfail="evaling transformed with undefined var in list fails",
        )

    def test_visit_binop(self, execute):
        op_map = {
            "+": ADD,
            "-": SUB,
            "*": MULT,
            "/": DIV,
            "//": FLOORDIV,
            "%": MOD,
            "**": POW,
            "<<": LSHIFT,
            ">>": RSHIFT,
            "|": BITOR,
            "^": BITXOR,
            "&": BITAND,
            "@": MATMUL,
        }
        for op in op_map:
            simple_op = f"a {op} 1"
            execute(
                simple_op,
                exec_transformed_xfail="evaling transformed with undefined var in op fails",
            )

    def test_visit_compare(self):
        op_map = {
            "==": EQ,
            "!=": NOTEQ,
            "<": LT,
            "<= ": LTE,
            ">": GT,
            ">=": GTE,
            "is": IS,
            "is not": ISNOT,
        }
        for op in op_map:
            simple_comp = f"a {op} b"
            expected_simple_comp = (
                f"lineapy_tracer.call(function_name='{op_map[op]}',"
                " syntax_dictionary={'lineno': 1,'col_offset': 0,"
                f" 'end_lineno': 1, 'end_col_offset': {len(op) + 4}}},"
                " arguments=[Variable('a'), Variable('b')],"
                " keyword_arguments=[])"
            )
            self._check_equality(simple_comp, expected_simple_comp)

        simple_in = "a in b"
        expected_simple_in = (
            "lineapy_tracer.call(function_name='"
            + IN
            + "', syntax_dictionary={'lineno': 1, 'col_offset': 0,"
            " 'end_lineno': 1, 'end_col_offset': 6},arguments=[Variable('b'),"
            " Variable('a')], keyword_arguments=[])"
        )
        self._check_equality(simple_in, expected_simple_in)

        simple_not_in = "a not in b"
        expected_simple_not_in = (
            "lineapy_tracer.call(function_name='"
            + NOT
            + "', syntax_dictionary={'lineno': 1,'col_offset': 0,"
            " 'end_lineno': 1, 'end_col_offset': 10},"
            " arguments=[lineapy_tracer.call(function_name='"
            + IN
            + "', syntax_dictionary={'lineno': 1, 'col_offset': 0,"
            " 'end_lineno': 1, 'end_col_offset':"
            " 10},arguments=[Variable('b'), Variable('a')],"
            " keyword_arguments=[])], keyword_arguments=[])"
        )
        self._check_equality(simple_not_in, expected_simple_not_in)

        chain_op = "a <= b < c"
        expected_chain_op = (
            "lineapy_tracer.call(function_name='"
            + LT
            + "', syntax_dictionary={'lineno': 1,'col_offset': 0,"
            "  'end_lineno':1, 'end_col_offset': 10},"
            " arguments=[lineapy_tracer.call(function_name='"
            + LTE
            + "', syntax_dictionary={'lineno': 1,'col_offset': 0, "
            " 'end_lineno':1, 'end_col_offset': 10},"
            " arguments=[Variable('a'), Variable('b')],"
            " keyword_arguments=[]), Variable('c')], keyword_arguments=[])"
        )
        self._check_equality(chain_op, expected_chain_op)

    def test_visit_subscript(self):
        simple = "ls[0]"
        expected = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "', syntax_dictionary={'lineno': 1,'col_offset': 0,"
            "  'end_lineno':1, 'end_col_offset': 5},"
            "arguments=[Variable('ls'), 0], keyword_arguments=[])"
        )
        self._check_equality(simple, expected)

        simple_var = "ls[a]"
        expected_var = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,"
            " 'end_col_offset':5},arguments=[Variable('ls'),Variable('a')],"
            " keyword_arguments=[])"
        )
        self._check_equality(simple_var, expected_var)

        simple_slice = "ls[1:2]"
        expected_simple_slice = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':7},"
            " arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='slice',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,"
            " 'end_col_offset':6},arguments=[1,2], keyword_arguments=[])],"
            " keyword_arguments=[])"
        )
        self._check_equality(simple_slice, expected_simple_slice)

        variable_slice = "ls[1:a]"
        expected_variable_slice = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':7},arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='slice',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},"
            " arguments=[1,Variable('a')], keyword_arguments=[])],"
            " keyword_arguments=[])"
        )
        self._check_equality(variable_slice, expected_variable_slice)

        simple_list = "ls[[1,2]]"
        expected_simple_list = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='__build_list__',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':8},arguments=[1,2],"
            " keyword_arguments=[])], keyword_arguments=[])"
        )
        self._check_equality(simple_list, expected_simple_list)

        variable_list = "ls[[1,a]]"
        expected_variable_list = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='__build_list__',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':8},arguments=[1,Variable('a')],"
            " keyword_arguments=[])], keyword_arguments=[])"
        )
        self._check_equality(variable_list, expected_variable_list)

    def test_visit_assign_subscript(self):
        simple_assign = "ls[0] = 1"
        expected_simple_assign = (
            "lineapy_tracer.call(function_name='"
            + SET_ITEM
            + "', syntax_dictionary={'lineno': 1, 'col_offset': 0,"
            " 'end_lineno': 1, 'end_col_offset':"
            " 9},arguments=[Variable('ls'), 0, 1], keyword_arguments=[])"
        )
        self._check_equality(simple_assign, expected_simple_assign)

        simple_variable_assign = "ls[a] = b"
        expected_variable_assign = (
            "lineapy_tracer.call(function_name='"
            + SET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},arguments=[Variable('ls'),"
            " Variable('a'), Variable('b')], keyword_arguments=[])"
        )
        self._check_equality(simple_variable_assign, expected_variable_assign)

        simple_slice_assign = "ls[1:2] = [1]"
        expected_simple_slice_assign = (
            "lineapy_tracer.call(function_name='"
            + SET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':13},arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='slice',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},arguments=[1,2],"
            " keyword_arguments=[]),lineapy_tracer.call(function_name='__build_list__',syntax_dictionary={'lineno':1,'col_offset':10,'end_lineno':1,'end_col_offset':13},arguments=[1],"
            " keyword_arguments=[])], keyword_arguments=[])"
        )
        self._check_equality(simple_slice_assign, expected_simple_slice_assign)

        variable_slice_assign = "ls[1:a] = [b]"
        expected_variable_slice_assign = (
            "lineapy_tracer.call(function_name='"
            + SET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':13},arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='slice',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},arguments=[1,Variable('a')],"
            " keyword_arguments=[]),lineapy_tracer.call(function_name='__build_list__',syntax_dictionary={'lineno':1,'col_offset':10,'end_lineno':1,'end_col_offset':13},arguments=[Variable('b')],"
            " keyword_arguments=[])], keyword_arguments=[])"
        )
        self._check_equality(
            variable_slice_assign, expected_variable_slice_assign
        )

        simple_list_assign = "ls[[1,2]] = [1,2]"
        expected_simple_list_assign = (
            "lineapy_tracer.call(function_name='"
            + SET_ITEM
            + "',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':17},arguments=[Variable('ls'),"
            " lineapy_tracer.call(function_name='__build_list__',syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':8},arguments=[1,2],"
            " keyword_arguments=[]),lineapy_tracer.call(function_name='__build_list__',syntax_dictionary={'lineno':1,'col_offset':12,'end_lineno':1,'end_col_offset':17},arguments=[1,2],"
            " keyword_arguments=[])], keyword_arguments=[])"
        )
        self._check_equality(simple_list_assign, expected_simple_list_assign)

    def test_linea_publish_visit_call(self):
        publish_code = "lineapy.linea_publish(a)"
        expected = "lineapy_tracer.publish(variable_name='a')"
        self._check_equality(publish_code, expected)
        publish_code_with_comment = "lineapy.linea_publish(a, 'test artifact')"
        expected_with_comment = (
            "lineapy_tracer.publish(variable_name='a', description='test"
            " artifact')"
        )
        self._check_equality(publish_code_with_comment, expected_with_comment)

    def test_headless_literal(self):
        expected = (
            "lineapy_tracer.headless_literal(1, "
            + "{'lineno': 1, 'col_offset': 0,"
            + "'end_lineno': 1, 'end_col_offset': 1})"
        )
        headless_code = "1"
        self._check_equality(headless_code, expected)

    def test_headless_variable(self):
        expected = (
            "lineapy_tracer.headless_variable"
            + "('b', {'lineno': 1, 'col_offset': 0,"
            + "'end_lineno': 1, 'end_col_offset': 1})"
        )
        headless_code = "b"
        self._check_equality(headless_code, expected)

    def test_literal_assignment(self):
        expected = (
            "lineapy_tracer.literal(assigned_variable_name='b', value=2,"
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            "'end_col_offset': 5})"
        )
        assignment_code = "b = 2"
        self._check_equality(assignment_code, expected)
