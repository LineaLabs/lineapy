from ast import parse

from astor import to_source

from lineapy.transformer.node_transformer import NodeTransformer
from tests.stub_data.graph_with_import import import_code
from tests.util import compare_ast


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
        assert new_code == expected_transformed

    def test_visit_import(self):
        simple_import = "import pandas"
        simple_expected = "lineapy_tracer.trace_import(name=\'pandas\', code=\'import pandas\', alias=None)\n"
        self._check_equality(simple_import, simple_expected)
        alias_import = "import pandas as pd"
        alias_expected = "lineapy_tracer.trace_import(name=\'pandas\', code=\'import pandas as pd\',\n    alias=\'pd\')\n"
        self._check_equality(alias_import, alias_expected)
        # multiple_imports = "import os, time"
        # multiple_expected = ""
        # self._check_equality(multiple_imports, multiple_expected)

    def test_visit_importfrom(self):
        expected = "lineapy_tracer.trace_import(name='math', code='from math import pow, sqrt',\n    attributes={'pow': '', 'sqrt': ''})\n"
        self._check_equality(import_code, expected)

    def test_visit_call(self):
        pass

    def test_visit_assign(self):
        pass
