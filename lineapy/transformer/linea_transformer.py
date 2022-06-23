import ast
import logging
from pathlib import Path
from types import ModuleType
from typing import Optional, Union
from winreg import KEY_WOW64_32KEY

from lineapy.data.types import (
    LineaCallNode,
    Node,
    SourceCode,
    SourceCodeLocation,
    SourceLocation,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.utils import get_new_id

logger = logging.getLogger(__name__)


class LineaTransformer(ast.NodeTransformer):
    def __init__(
        self,
        code: str,
        location: SourceCodeLocation,
        tracer: Tracer,
    ):
        self.source_code = SourceCode(
            id=get_new_id(), code=code, location=location
        )
        # tracer.db.write_source_code(self.source_code)
        self.tracer = tracer
        # Set __file__ to the pathname of the file
        if isinstance(location, Path):
            tracer.executor.module_file = str(location)
        # The result of the last line, a node if it was an expression,
        # None if it was a statement. Used by ipython to grab the last value
        self.last_statement_result: Optional[Node] = None

    def lgeneric_visit(self, node: ast.AST):
        return node

    def lvisit(self, node):
        """Visit a node."""
        method = "lvisit_" + node.__class__.__name__
        visitor = getattr(self, method, self.lgeneric_visit)
        return visitor(node)

    def visit_Call(self, node: ast.Call) -> Union[ast.Call, LineaCallNode]:
        func = self.lvisit(node.func)
        if func is not None and func[0] == "lineapy":
            argument_values = [self.lvisit(arg) for arg in node.args]
            # keyword_values = {key:value for }
            if func[1] == "save":
                artifact_name = argument_values[1]
                # this is to locate this node in the graph. its predecessors
                # are the var we are trying to save as an artifact
                dependent = self.tracer.lookup_node(
                    argument_values[0], self.get_source(node)
                )
            if func[1] == "get":
                artifact_name = argument_values[0]

            lineanode = LineaCallNode(
                id=get_new_id(),
                session_id=self.tracer.get_session_id(),
                function_id=get_new_id(),
                artifact_name=artifact_name,
                artifact_version=None,
                positional_args=[dependent],  # there can only be one - for now
                keyword_args=[],
                module_name=func[0],
                function_name=func[1],
            )

            # TODO - save the artifact here and attach the result to the graph.
            print(
                "I'm gonna do it.. i'm gonna save the artifact here. ready or not"
            )
            return lineanode

        return node

    def lvisit_Attribute(self, node: ast.Attribute):
        value = self.lvisit(node.value)
        if value in self.tracer.variable_name_to_node:
            module_imported: ModuleType = self.tracer.executor.get_value(  # type: ignore
                self.tracer.variable_name_to_node[value].id
            )
            module_name = module_imported.__name__
            attribute = node.attr
            return (module_name, attribute)
        return None

    def lvisit_Name(self, node):
        return node.id

    def lvisit_Constant(self, node):
        # name of the artifact etc
        return node.value

    def get_source(self, node: ast.AST) -> Optional[SourceLocation]:
        if not hasattr(node, "lineno"):
            return None
        return SourceLocation(
            source_code=self.source_code,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=node.end_lineno,  # type: ignore
            end_col_offset=node.end_col_offset,  # type: ignore
        )
