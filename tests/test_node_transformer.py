import ast

import astor

from lineapy.constants import *
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
            internal_warning_log("Transformed code:\t" + astor.to_source(new_tree))
            internal_warning_log("Expected code:\t" + astor.to_source(expected_tree))
            assert False

    def test_visit_import(self):
        simple_import = "import pandas"
        simple_expected = (
            "lineapy_tracer.trace_import(name='pandas', "
            "syntax_dictionary={'lineno': 1,"
            "'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 13},"
            " alias=None)"
        )
        self._check_equality(simple_import, simple_expected)
        alias_import = "import pandas as pd"
        alias_expected = (
            "lineapy_tracer.trace_import(name='pandas',"
            " syntax_dictionary={'lineno':1,"
            " 'col_offset':0,'end_lineno':1,'end_col_offset':19},   "
            " alias='pd')"
        )
        self._check_equality(alias_import, alias_expected)
        # multiple_imports = "import os, time"
        # multiple_expected = ""
        # self._check_equality(multiple_imports, multiple_expected)

    def test_visit_importfrom(self):
        expected = (
            "lineapy_tracer.trace_import(name='math', "
            " syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 43},    attributes={'pow': 'power', 'sqrt':"
            " 'root'})"
        )
        self._check_equality(import_code, expected)

    def test_visit_call(self):
        simple_call = "foo()"
        expected_simple_call = (
            "lineapy_tracer.call(function_name='foo',"
            " syntax_dictionary={'lineno': 1,"
            + "'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 5},"
            " arguments=[])"
        )
        self._check_equality(simple_call, expected_simple_call)

        call_with_args = "foo(a, b)"
        expected_call_with_args = (
            "lineapy_tracer.call(function_name='foo',"
            " syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 9}, arguments=[Variable('a'), Variable('b')])"
        )
        self._check_equality(call_with_args, expected_call_with_args)

        call_with_keyword_args = "foo(b=1)"  # FIXME currently unsupported

    def test_visit_assign(self):
        simple_assign = "a = 1"
        expected_simple_assign = (
            "lineapy_tracer.assign(variable_name='a', value_node=1, "
            + "syntax_dictionary={"
            + "'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 5})"
        )
        self._check_equality(simple_assign, expected_simple_assign)

        assign_variable = "a = foo"
        expected_assign_variable = (
            "lineapy_tracer.assign(variable_name='a',"
            " value_node=Variable('foo'),"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':7})"
        )
        self._check_equality(assign_variable, expected_assign_variable)

    def test_visit_list(self):
        simple_list = "[1, 2]"
        expected_simple_list = (
            "lineapy_tracer.call(function_name='__build_list__',"
            " syntax_dictionary={" + "'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 6}," + "arguments=[1, 2])"
        )
        self._check_equality(simple_list, expected_simple_list)

        variable_list = "[1, a]"
        expected_variable_list = (
            "lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            "'end_col_offset': 6}, arguments=[1, Variable('a')])"
        )
        self._check_equality(variable_list, expected_variable_list)

    def test_visit_binop(self):
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
            expected_simple_op = (
                f"lineapy_tracer.call(function_name='{op_map[op]}', "
                f"syntax_dictionary={{'lineno': 1,'col_offset': 0, 'end_lineno': 1, "
                f"'end_col_offset': {len(op) + 4}}}, "
                "arguments=[Variable('a'), 1])"
            )
            self._check_equality(simple_op, expected_simple_op)

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
                f"lineapy_tracer.call(function_name='{op_map[op]}', "
                f"syntax_dictionary={{'lineno': 1,'col_offset': 0, 'end_lineno': 1, "
                f"'end_col_offset': {len(op) + 4}}}, "
                "arguments=[Variable('a'), Variable('b')])"
            )
            self._check_equality(simple_comp, expected_simple_comp)

        simple_in = "a in b"
        expected_simple_in = (
            "lineapy_tracer.call(function_name='" + IN + "', "
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 6},"
            "arguments=[Variable('b'), Variable('a')])"
        )
        self._check_equality(simple_in, expected_simple_in)

        simple_not_in = "a not in b"
        expected_simple_not_in = (
            "lineapy_tracer.call(function_name='" + NOT + "', "
            "syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 10}, "
            "arguments=[lineapy_tracer.call(function_name='" + IN + "', "
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 10},"
            "arguments=[Variable('b'), Variable('a')])])"
        )
        self._check_equality(simple_not_in, expected_simple_not_in)

        chain_op = "a <= b < c"
        expected_chain_op = (
            "lineapy_tracer.call(function_name='" + LT + "', "
            "syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 10}, "
            "arguments=[lineapy_tracer.call(function_name='" + LTE + "', "
            "syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 10}, "
            "arguments=[Variable('a'), Variable('b')]), Variable('c')])"
        )
        self._check_equality(chain_op, expected_chain_op)

    def test_visit_subscript(self):
        simple = "ls[0]"
        expected = (
            "lineapy_tracer.call(function_name='"
            + GET_ITEM
            + "', syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 5},  arguments=[Variable('ls'), 0])"
        )
        self._check_equality(simple, expected)

        simple_var = "ls[a]"
        expected_var = (
            "lineapy_tracer.call(function_name='" + GET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':5},"
            "arguments=[Variable('ls'), Variable('a')])"
        )
        self._check_equality(simple_var, expected_var)

        simple_slice = "ls[1:2]"
        expected_simple_slice = (
            "lineapy_tracer.call(function_name='" + GET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':7},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='slice',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},arguments=[1,2])])"
        )
        self._check_equality(simple_slice, expected_simple_slice)

        variable_slice = "ls[1:a]"
        expected_variable_slice = (
            "lineapy_tracer.call(function_name='" + GET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':7},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='slice',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},"
            "arguments=[1,Variable('a')])])"
        )
        self._check_equality(variable_slice, expected_variable_slice)

        simple_list = "ls[[1,2]]"
        expected_simple_list = (
            "lineapy_tracer.call(function_name='" + GET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':8},"
            "arguments=[1,2])])"
        )
        self._check_equality(simple_list, expected_simple_list)

        variable_list = "ls[[1,a]]"
        expected_variable_list = (
            "lineapy_tracer.call(function_name='" + GET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':8},"
            "arguments=[1,Variable('a')])])"
        )
        self._check_equality(variable_list, expected_variable_list)

    def test_visit_assign_subscript(self):
        simple_assign = "ls[0] = 1"
        expected_simple_assign = (
            "lineapy_tracer.call(function_name='" + SET_ITEM + "', "
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 9},"
            "arguments=[Variable('ls'), 0, 1])"
        )
        self._check_equality(simple_assign, expected_simple_assign)

        simple_variable_assign = "ls[a] = b"
        expected_variable_assign = (
            "lineapy_tracer.call(function_name='" + SET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},"
            "arguments=[Variable('ls'), Variable('a'), Variable('b')])"
        )
        self._check_equality(simple_variable_assign, expected_variable_assign)

        simple_slice_assign = "ls[1:2] = [1]"
        expected_simple_slice_assign = (
            "lineapy_tracer.call(function_name='" + SET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':13},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='slice',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},"
            "arguments=[1,2]),"
            "lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno':1,'col_offset':10,'end_lineno':1,'end_col_offset':13},arguments=[1])])"
        )
        self._check_equality(simple_slice_assign, expected_simple_slice_assign)

        variable_slice_assign = "ls[1:a] = [b]"
        expected_variable_slice_assign = (
            "lineapy_tracer.call(function_name='" + SET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':13},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='slice',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':6},"
            "arguments=[1,Variable('a')]),"
            "lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno':1,'col_offset':10,'end_lineno':1,'end_col_offset':13},"
            "arguments=[Variable('b')])],)"
        )
        self._check_equality(variable_slice_assign, expected_variable_slice_assign)

        simple_list_assign = "ls[[1,2]] = [1,2]"
        expected_simple_list_assign = (
            "lineapy_tracer.call(function_name='" + SET_ITEM + "',"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':17},"
            "arguments=[Variable('ls'), lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno':1,'col_offset':3,'end_lineno':1,'end_col_offset':8},"
            "arguments=[1,2]),lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno':1,'col_offset':12,'end_lineno':1,'end_col_offset':17},"
            "arguments=[1,2])])"
        )
        self._check_equality(simple_list_assign, expected_simple_list_assign)

    def test_linea_publish_visit_call(self):
        publish_code = "lineapy.linea_publish(a)"
        expected = "lineapy_tracer.publish(variable_name='a')"
        self._check_equality(publish_code, expected)
        publish_code_with_comment = "lineapy.linea_publish(a, 'test artifact')"
        expected_with_comment = (
            "lineapy_tracer.publish(variable_name='a', description='test" " artifact')"
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
            "lineapy_tracer.assign(variable_name='b', value_node=2,"
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1, "
            "'end_col_offset': 3})"
        )
        assignment_code = "b=2"
        self._check_equality(assignment_code, expected)
