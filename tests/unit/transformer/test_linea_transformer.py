import ast
import sys

import asttokens
import pytest
from astpretty import pprint
from mock import MagicMock, patch

import lineapy
from lineapy.data.types import LineaCallNode, SessionType
from lineapy.db.db import RelationalLineaDB
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.linea_transformer import LineaTransformer
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.transformer.source_giver import SourceGiver
from lineapy.transformer.transform_code import transform
from lineapy.utils.config import options


def _get_ast_node(code):
    node = ast.parse(code)
    if sys.version_info < (3, 8):  # give me endlines!
        asttokens.ASTTokens(code, parse=False, tree=node)
        SourceGiver().transform(node)

    return node


class TestLineaTransformer:
    lt: LineaTransformer

    @pytest.fixture(autouse=True)
    def before_everything(self):
        db = RelationalLineaDB.from_config(options)
        tracer = Tracer(db, SessionType.SCRIPT)
        # tracermock = MagicMock()
        # imports_dict = {"lineapy": lineapy}
        # tracermock.module_name_to_node.__getitem__.side_effect = (
        #     imports_dict.__getitem__
        # )
        # tracermock.module_name_to_node.__contains__.side_effect = (
        #     imports_dict.__contains__
        # )
        nt = NodeTransformer("", MagicMock(), tracer)
        lt = LineaTransformer("", MagicMock(), tracer)
        assert lt is not None
        assert nt is not None
        self.nt = nt
        self.lt = lt

    def test_basic_linea_save(self):
        import_node = _get_ast_node(
            """import lineapy
x=1
"""
        )
        self.nt.visit(import_node)
        test_node = _get_ast_node(
            """
lineapy.save(x,"x")
"""
        )
        pprint(test_node.body[0].value)
        ret_node: LineaCallNode = self.lt.visit(test_node.body[0].value)
        assert ret_node.artifact_name == "x"
        assert ret_node.function_name == "save"
        assert ret_node.module_name == "lineapy"

    def test_linea_alias(self):
        import_node = _get_ast_node(
            """import lineapy as lp
x=1
"""
        )
        self.nt.visit(import_node)
        test_node = _get_ast_node(
            """
lp.save(x,"x")
"""
        )
        pprint(test_node.body[0].value)
        ret_node: LineaCallNode = self.lt.visit(test_node.body[0].value)
        assert ret_node.artifact_name == "x"
        assert ret_node.function_name == "save"
        assert ret_node.module_name == "lineapy"

    def test_linea_functions_imported(self):
        import_node = _get_ast_node(
            """from lineapy import save as sv
x=1
"""
        )
        self.nt.visit(import_node)
        test_node = _get_ast_node(
            """
sv(x,"x")
"""
        )
        pprint(test_node.body[0].value)
        ret_node: LineaCallNode = self.lt.visit(test_node.body[0].value)
        assert ret_node.artifact_name == "x"
        assert ret_node.function_name == "save"
        assert ret_node.module_name == "lineapy"

    def test_other_call_fn_not_modified(self):
        import_node = _get_ast_node(
            """import math
"""
        )
        self.nt.visit(import_node)
        test_node = _get_ast_node(
            """
a = math.sqrt(4)
"""
        )
        pprint(test_node.body[0].value)
        ret_node: LineaCallNode = self.lt.visit(test_node.body[0].value)
        assert ret_node.artifact_name == "x"
        assert ret_node.function_name == "save"
        assert ret_node.module_name == "lineapy"
