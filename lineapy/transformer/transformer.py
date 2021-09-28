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
        self.has_initiated = False

    def transform(
        self,
        code: str,
        session_type: SessionType,
        execution_mode: ExecutionMode,
        session_name: str,
    ):
        info_log("transform", code)
        if not self.has_initiated:
            self.tracer = Tracer(session_type, session_name, execution_mode)
            self.has_initiated = True

        self.transform_user_code(code)
        if session_type in [SessionType.SCRIPT, SessionType.STATIC]:
            self.create_exit()
        else:
            raise CaseNotHandledError(f"{session_type.name} not supported")

        # pprint(transformed_tree, show_offsets=False)
        # transformed_code = to_source(transformed_tree)
        # return transformed_code

    def transform_user_code(self, code: str):
        # FIXME: just a pass thru for now
        node_transformer = NodeTransformer(code, self.tracer)
        tree = ast.parse(code)
        node_transformer.visit(tree)
        # return new_tree

    def set_active_cell(self, cell_id):
        pass

    def create_exit(self):
        """
        Hack: just returning raw string for now... We can invest in nodes
          if there is a feature that requires such.
        NOTE: maybe we could move this to a standalone function
        """
        self.tracer.exit()
