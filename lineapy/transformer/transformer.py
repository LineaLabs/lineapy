import ast

from lineapy.constants import (
    ExecutionMode,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.data.types import SessionType, SourceCodeLocation
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.utils import CaseNotHandledError
from pathlib import Path

# TODO: We should probably just remove this class, and use the NodeTransformer
# directly
class Transformer:
    """
    The reason why we have the transformer and the instrumentation
      separate is that we need runtime information when creating the nodes.
    If we created the instrumentation statically, then the node-level
      information would be lost.
    """

    def transform(
        self,
        code: str,
        session_type: SessionType,
        execution_mode: ExecutionMode,
        path: str,
    ) -> Tracer:
        tracer = Tracer(session_type, execution_mode, session_name=None)

        node_transformer = NodeTransformer(code, Path(path), tracer)
        tree = ast.parse(code)
        node_transformer.visit(tree)
        if session_type in [SessionType.SCRIPT, SessionType.STATIC]:
            tracer.exit()
        else:
            raise CaseNotHandledError(f"{session_type.name} not supported")
        return tracer
