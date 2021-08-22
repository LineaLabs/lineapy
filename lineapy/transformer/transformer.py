from typing import Any, List
import ast

# some constants
LINEAPY_TRACER_NAME = "lineapy_tracer"
LINEAPY_IMPORT_LIB_NAME = "lineapy"
# FIXME: find the typing for AST nodes
NodeType = Any


class Transformer:
    """
    The reason why we have the transformer and the instrumentation separate is that we need runtime information when creating the nodes.
    If we created the instrumentation statically, then the node level information would be lost.
    """

    def __init__(self):
        self.has_initiated = False

    def transform(self, code: str, one_shot=True) -> str:
        body = self.transform_user_code(code)
        if one_shot:
            return
        return body

    def transform_user_code(self, code: str) -> List[NodeType]:
        pass

    def create_exit(self) -> List[NodeType]:
        """
        Hack: just returning raw string for now... We can invest in nodes if there is a feature that requires such.
        note maybe we could move this to a standalone function
        """
        return "lineapy.exit()\n"

    def create_enter(self) -> List[NodeType]:
        """
        Also a hack for now...
        """
        import_node = (
            ast.Import(
                names=[ast.alias(name="lineapy")],
            ),
        )
        tracer_node = ast.Assign(
            id="lineapy_tracer",
            ctx=ast.Store(),
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="lineapy", ctx=ast.Load()),
                    attr="Tracer",
                    ctx=ast.Load(),
                )
            ),
        )
        return [import_node, tracer_node]
