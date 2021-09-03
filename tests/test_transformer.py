from ast import NodeTransformer, parse
from astor import to_source

from tests.util import compare_ast
from tests.stub_data.graph_with_import import import_code


class NodeTransformerTest:
    # we might need some setup in the future, but for this one we are fine
    def sanity_check_compare_ast(self):
        code = "import math\na = 1"
        tree1 = parse(code)
        tree2 = parse(code)
        assert compare_ast(tree1, tree2)

    def transform_import(self):
        node_transformer = NodeTransformer()
        tree = parse(import_code)
        new_tree = node_transformer.visit(tree)
        new_code = to_source(new_tree)
        pass
