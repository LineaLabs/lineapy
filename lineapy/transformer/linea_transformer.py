import ast
import logging
from pathlib import Path
from types import ModuleType
from typing import Optional, Union

from lineapy.api.api import _artifact_store, _get, _save, healthcheck
from lineapy.data.types import (
    LineaCallNode,
    Node,
    PositionalArgument,
    SourceCode,
    SourceCodeLocation,
    SourceLocation,
)
from lineapy.exceptions.db_exceptions import ArtifactSaveException
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

    def visit_Call(
        self, node: ast.Call
    ) -> Union[None, ast.Call, LineaCallNode]:
        func = self.lvisit(node.func)
        if func is not None and func[0] == "lineapy":
            args_to_pass = []
            to_exec = healthcheck
            artifact_name: Optional[str] = None
            argument_values = [self.lvisit(arg) for arg in node.args]
            dependent = []
            # keyword_values = {key:value for }
            if func[1] == "save":
                artifact_name = argument_values[1]
                # this is to locate this node in the graph. its predecessors
                # are the var we are trying to save as an artifact
                # there can only be one - for now
                arg = argument_values[0]
                if isinstance(arg, tuple):
                    # if this happens the artifact you are trying to save is a lineapy function/var like external state etc.
                    # in that case, we pick the actual attribute.
                    arg = argument_values[0][3]
                    argnode = self.tracer.executor._value_to_node[arg]
                else:
                    argnode = self.tracer.lookup_node(arg, None).id
                # TODO - might not need to look up the latest mutated node here. will revisit
                argnode_latest = (
                    self.tracer.mutation_tracker.get_latest_mutate_node(
                        argnode
                    )
                )
                dependent = [argnode_latest]
                args_to_pass = [
                    self.tracer.executor.get_value(argnode_latest),
                    argument_values[1],
                ]
                to_exec = _save  # type: ignore
            if func[1] == "get":
                artifact_name = argument_values[0]
                args_to_pass = [artifact_name]
                to_exec = _get  # type: ignore

            if func[1] == "artifact_store":
                to_exec = _artifact_store  # type:ignore

            lineanode = LineaCallNode(
                id=get_new_id(),
                session_id=self.tracer.get_session_id(),
                # function_id=get_new_id(),
                artifact_name=artifact_name,
                artifact_version=None,
                positional_args=[
                    PositionalArgument(
                        id=d,
                        starred=False,
                    )
                    for d in dependent
                ],
                keyword_args=[],
                module_name=func[0],
                function_name=func[1],
            )

            # TODO - save the artifact here and attach the result to the graph.
            print(
                "I'm gonna do it.. i'm gonna save the artifact here. ready or not"
            )
            print(artifact_name, args_to_pass)
            args_to_pass = [
                lineanode,
                self.tracer.executor,
                self.tracer.db,
            ] + args_to_pass
            print(to_exec)
            # set the equivalent of
            try:
                value = to_exec(*args_to_pass)
                # the tracer dict linea_node_id_to_value preserves linea nodes across runs
                self.tracer.linea_node_id_to_value[lineanode.id] = value
                # the executor dict is the one that are used during execution. the tracer
                # dict containing linea node values gets copied over pre-populating the executor
                self.tracer.executor._id_to_value[lineanode.id] = value
            except ArtifactSaveException as exc_info:
                logger.error("Artifact could not be saved.")
                logger.debug(exc_info)
                return node

            return lineanode

        return node

    def lvisit_Attribute(self, node: ast.Attribute):
        value = self.lvisit(node.value)
        # if the module is in our imports list - because we only care about lineapy,
        # we will simply bother with this dict and ignore others
        if value in self.tracer.module_name_to_node:
            module_imported: ModuleType = self.tracer.executor.get_value(  # type: ignore
                self.tracer.module_name_to_node[value].id
            )
            module_name = module_imported.__name__
            attribute = getattr(module_imported, node.attr)
            attribute_name = attribute.__name__
            return (module_name, attribute_name, module_imported, attribute)
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
