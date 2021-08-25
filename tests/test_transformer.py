from ast import NodeTransformer, parse
from lineapy.graph_reader.graph_util import are_nodes_conetent_equal
from astor import to_source

from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.transformer import LINEAPY_TRACER_NAME
from tests.util import compare_ast
from tests.stub_data.graph_with_import import import_code, import_math_node


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
        t = Tracer()
        scope = {LINEAPY_TRACER_NAME: t}
        # using exec but setting the scope and relying on the side-effect of tracer class
        exec(new_code, scope)
        imported_node = t.records_manager.records_pool[0]
        assert are_nodes_conetent_equal(imported_node, import_math_node)
        print(imported_node)
