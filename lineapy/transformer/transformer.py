import ast
from pathlib import Path

from lineapy.constants import ExecutionMode
from lineapy.data.types import SessionType
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer


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
        tracer.exit()
        return tracer
