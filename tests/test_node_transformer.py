from ast import parse
from astor import to_source

from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.utils import internal_warning_log
from tests.stub_data.graph_with_import import import_code
from tests.util import compare_ast, strip_non_letter_num


class TestNodeTransformer:
    # we might need some setup in the future, but for this one we are fine
    def test_compare_ast(self):
        code1 = "import math\na = 1"
        code2 = "import math\na =    1"
        code3 = "import math\na = 1"
        tree1 = parse(code1)
        tree2 = parse(code2)
        tree3 = parse(code3)
        assert compare_ast(tree1, tree2)
        assert compare_ast(tree1, tree3)

    @staticmethod
    def _check_equality(original_code: str, expected_transformed: str) -> None:
        node_transformer = NodeTransformer(original_code)
        tree = parse(original_code)
        new_tree = node_transformer.visit(tree)
        new_code = to_source(new_tree)
        new_code_stripped = strip_non_letter_num(new_code)
        expected_transformed_stripped = strip_non_letter_num(expected_transformed)
        if new_code_stripped != expected_transformed_stripped:
            internal_warning_log(new_code_stripped)
            internal_warning_log(expected_transformed_stripped)
            assert False

    def test_visit_import(self):
        simple_import = "import pandas"
        simple_expected = (
            "lineapy_tracer.trace_import(name='pandas', "
            "syntax_dictionary={'lineno': 1,"
            "'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 13},"
            " alias=None)\n"
        )
        self._check_equality(simple_import, simple_expected)
        alias_import = "import pandas as pd"
        alias_expected = (
            "lineapy_tracer.trace_import(name='pandas',"
            " syntax_dictionary={'lineno':1,"
            " 'col_offset':0,'end_lineno':1,'end_col_offset':19},\n   "
            " alias='pd')\n"
        )
        self._check_equality(alias_import, alias_expected)
        # multiple_imports = "import os, time"
        # multiple_expected = ""
        # self._check_equality(multiple_imports, multiple_expected)

    def test_visit_importfrom(self):
        expected = (
            "lineapy_tracer.trace_import(name='math', "
            " syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 43},\n    attributes={'pow': 'power', 'sqrt':"
            " 'root'})\n"
        )
        self._check_equality(import_code, expected)

    def test_visit_call(self):
        simple_call = "foo()"
        expected_simple_call = (
            "lineapy_tracer.call(function_name='foo',"
            " syntax_dictionary={'lineno': 1,\n"
            + "'col_offset': 0, 'end_lineno': 1, 'end_col_offset': 5},"
            " arguments=[])\n"
        )
        self._check_equality(simple_call, expected_simple_call)

        call_with_args = "foo(a, b)"
        expected_call_with_args = (
            "lineapy_tracer.call(function_name='foo',"
            " syntax_dictionary={'lineno': 1,'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 9}, arguments=[Variable('a'), Variable('b')])\n"
        )
        self._check_equality(call_with_args, expected_call_with_args)

        call_with_keyword_args = "foo(b=1)"  # FIXME currently unsupported

    def test_visit_assign(self):
        simple_assign = "a = 1"
        expected_simple_assign = (
            "lineapy_tracer.assign(variable_name='a', value_node=1, "
            + "syntax_dictionary={\n"
            + "'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 5})\n"
        )
        self._check_equality(simple_assign, expected_simple_assign)

        assign_variable = "a = foo"
        expected_assign_variable = (
            "lineapy_tracer.assign(variable_name='a',"
            " value_node=Variable('foo'),"
            "syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':7})\n"
        )
        self._check_equality(assign_variable, expected_assign_variable)

    def test_visit_list(self):
        simple_list = "[1, 2]"
        expected_simple_list = (
            "lineapy_tracer.call(function_name='__build_list__',"
            " syntax_dictionary={" + "'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 6}," + "arguments=[1, 2])\n"
        )
        self._check_equality(simple_list, expected_simple_list)

        variable_list = "[1, a]"
        expected_variable_list = (
            "lineapy_tracer.call(function_name='__build_list__',"
            "syntax_dictionary={'lineno': 1, 'col_offset': 0, 'end_lineno': 1,"
            "'end_col_offset': 6}, arguments=[1, Variable('a')])\n"
        )
        self._check_equality(variable_list, expected_variable_list)

    def test_visit_binop(self):
        op_map = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "truediv",
            "//": "floordiv",
            "%": "mod",
            "**": "pow",
            "<<": "lshift",
            ">>": "rshift",
            "|": "or_",
            "^": "xor",
            "&": "and_",
            "@": "matmul",
        }
        for op in op_map:
            simple_op = f"a {op} 1"
            expected_simple_op = (
                f"lineapy_tracer.call(function_name='{op_map[op]}',syntax_dictionary={{'lineno':"
                " 1,'col_offset': 0, 'end_lineno': 1, 'end_col_offset':"
                f" {len(op) + 4}}},  arguments=[Variable('a'), 1])\n"
            )
            self._check_equality(simple_op, expected_simple_op)

    def test_subscript(self):
        simple = "ls[0]"
        expected = (
            "lineapy_tracer.call(function_name='getitem', syntax_dictionary={  "
            "              'lineno': 1,'col_offset': 0, 'end_lineno': 1,"
            " 'end_col_offset': 5},  arguments=[Variable('ls'), 0])\n"
        )
        self._check_equality(simple, expected)

        simple_var = "ls[a]"
        expected_var = (
            "lineapy_tracer.call(function_name='getitem',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':5},arguments=[Variable('ls'),"
            " Variable('a')])\n"
        )
        self._check_equality(simple_var, expected_var)

        simple_assign = "ls[0] = 1"
        expected_simple_assign = (
            "lineapy_tracer.call(function_name='setitem',syntax_dictionary={'lineno':1,'col_offset':0,'end_lineno':1,'end_col_offset':9},arguments=[Variable('ls'),"
            " 0, 1])\n"
        )
        self._check_equality(simple_assign, expected_simple_assign)

    def test_lean_publish_visit_call(self):
        publish_code = "lineapy.linea_publish(a)"
        expected = "lineapy_tracer.publish(variable_name='a')\n"
        self._check_equality(publish_code, expected)
        publish_code_with_comment = "lineapy.linea_publish(a, 'test artifact')"
        expected_with_comment = (
            "lineapy_tracer.publish(variable_name='a', description='test"
            " artifact')\n"
        )
        self._check_equality(publish_code_with_comment, expected_with_comment)
