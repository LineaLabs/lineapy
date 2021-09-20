import ast
from typing import List, Optional
from astor import to_source

from lineapy.constants import (
    LINEAPY_IMPORT_LIB_NAME,
    LINEAPY_TRACER_CLASS,
    LINEAPY_TRACER_NAME,
    ExecutionMode,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.instrumentation.variable import Variable
from lineapy.data.types import SessionType
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.utils import CaseNotHandledError, info_log

# FIXME: find the typing for AST nodes
TreeNodeType = ast.AST


# FIXME: add typing
def append_code_to_tree(
    source: ast.Module,
    to_append: List[TreeNodeType],
    is_beginning: bool = False,
) -> ast.Module:
    if is_beginning:
        source.body = to_append + source.body
    else:
        source.body = source.body + to_append
    return source


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
        session_name: Optional[str] = None,
    ) -> str:
        info_log("transform", code)
        transformed_tree = self.transform_user_code(code)
        if not self.has_initiated:
            enter_tree = self.create_enter(
                session_type,
                session_name,
                execution_mode,
            )
            append_code_to_tree(
                transformed_tree,
                enter_tree,
                is_beginning=True,
            )
            self.has_initiated = True

        if session_type in [SessionType.SCRIPT, SessionType.STATIC]:
            exit_tree = self.create_exit()
            append_code_to_tree(transformed_tree, exit_tree)
        else:
            raise CaseNotHandledError(f"{session_type.name} not supported")

        # pprint(transformed_tree, show_offsets=False)
        transformed_code = to_source(transformed_tree)
        return transformed_code

    def transform_user_code(self, code: str) -> ast.Module:
        # FIXME: just a pass thru for now
        node_transformer = NodeTransformer(code)
        tree = ast.parse(code)
        new_tree = node_transformer.visit(tree)
        return new_tree

    def set_active_cell(self, cell_id):
        pass

    def create_exit(self) -> List[TreeNodeType]:
        """
        Hack: just returning raw string for now... We can invest in nodes
          if there is a feature that requires such.
        NOTE: maybe we could move this to a standalone function
        """
        return [
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                        attr="exit",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            )
        ]

    def create_enter(
        self,
        session_type: SessionType,
        session_name: Optional[str] = None,
        execution_mode: ExecutionMode = ExecutionMode.TEST,
    ) -> List[TreeNodeType]:
        import_node = ast.ImportFrom(
            module=LINEAPY_IMPORT_LIB_NAME,
            names=[
                ast.alias(name=SessionType.__name__, asname=None),
                ast.alias(name=Tracer.__name__, asname=None),
                ast.alias(name=Variable.__name__, asname=None),
                ast.alias(name=ExecutionMode.__name__, asname=None),
            ],
            level=0,
        )
        session_type_node = ast.Attribute(
            value=ast.Name(
                id=SessionType.__name__,
                ctx=ast.Load(),
            ),
            attr=session_type.name,
            ctx=ast.Load(),
        )

        execution_mode_node_attr = execution_mode.name
        execution_mode_node = ast.Attribute(
            value=ast.Name(
                id=ExecutionMode.__name__,
                ctx=ast.Load(),
            ),
            attr=execution_mode_node_attr,
            ctx=ast.Load(),
        )
        tracer_node = ast.Assign(
            id=LINEAPY_TRACER_NAME,
            ctx=ast.Store(),
            targets=[ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id=LINEAPY_TRACER_CLASS, ctx=ast.Load()),
                args=[
                    session_type_node,
                    ast.Constant(value=session_name),
                    execution_mode_node,
                ],
                keywords=[],
            ),
        )
        # pprint(tracer_node, show_offsets=False)
        return [import_node, tracer_node]
