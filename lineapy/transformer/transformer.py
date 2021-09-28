import ast

from lineapy.constants import (
    ExecutionMode,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.data.types import SessionType
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.utils import CaseNotHandledError, info_log


class Transformer:
    """
    The reason why we have the transformer and the instrumentation
      separate is that we need runtime information when creating the nodes.
    If we created the instrumentation statically, then the node-level
      information would be lost.
    """

    def __init__(self):
        self.tracer = None

    def transform(
        self,
        code: str,
        session_type: SessionType,
        execution_mode: ExecutionMode,
        session_name: str,
    ):
        info_log("transform", code)
        if not self.tracer:
            self.tracer = Tracer(session_type, session_name, execution_mode)

        node_transformer = NodeTransformer(code, self.tracer)
        tree = ast.parse(code)
        node_transformer.visit(tree)
        if session_type in [SessionType.SCRIPT, SessionType.STATIC]:
            self.tracer.exit()
        else:
            raise CaseNotHandledError(f"{session_type.name} not supported")

    def set_active_cell(self, cell_id):
        pass
