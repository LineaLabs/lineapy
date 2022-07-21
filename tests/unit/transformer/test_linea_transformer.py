import ast
import sys

import asttokens
import pytest
from mock import MagicMock, patch

import lineapy
from lineapy.data.types import LineaCallNode
from lineapy.transformer.linea_transformer import LineaTransformer
from lineapy.transformer.source_giver import SourceGiver
from lineapy.transformer.transform_code import transform


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
        tracermock = MagicMock()
        imports_dict = {"lineapy": lineapy}
        tracermock.module_name_to_node.__getitem__.side_effect = (
            imports_dict.__getitem__
        )
        tracermock.module_name_to_node.__contains__.side_effect = (
            imports_dict.__contains__
        )
        lt = LineaTransformer("", MagicMock(), tracermock)
        assert lt is not None
        self.lt = lt

    def test_basic_linea_save(self):
        test_node = _get_ast_node(
            """
import lineapy
lineapy.save(x,"x")
"""
        )
        ret_node: LineaCallNode = self.lt.visit(test_node.body[1].value)
        assert ret_node.artifact_name == "x"
        assert ret_node.function_name == "save"
        assert ret_node.module_name == "lineapy"
