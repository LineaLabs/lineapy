import ast
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, List, Optional, Union

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
from lineapy.internal.api import _artifact_store, _get, _save, healthcheck
from lineapy.utils.utils import get_new_id

logger = logging.getLogger(__name__)


class LINEA_ENDPOINTS(Enum):
    LINEAPY = "lineapy"
    SAVE = "save"
    GET = "get"
    ARTIFACT_STORE = "artifact_store"


LINEA_ENDPOINT_MAPPING = {
    LINEA_ENDPOINTS.SAVE: _save,
    LINEA_ENDPOINTS.GET: _get,
    LINEA_ENDPOINTS.ARTIFACT_STORE: _artifact_store,
}


@dataclass
class FunctionObj:
    # module: ModuleType
    module_name: Optional[str]
    func: Any

    def get_module_name(self) -> Optional[str]:
        if (
            self.module_name is not None
        ):  # and hasattr(self.module, "__name__"):
            return self.module_name

        return None

    def get_function_name(self):
        if self.func is not None and hasattr(self.func, "__name__"):
            return self.func.__name__
        return None

    def compare_names(self, ours, theirs) -> bool:
        if ours is not None:
            return ours == theirs
        return False

    def check_function_name(self, name_to_compare) -> bool:
        our_name = self.get_function_name()
        return self.compare_names(our_name, name_to_compare)

    def check_module_name(self, name_to_compare) -> bool:
        our_name = self.get_module_name()
        # check if starts with instead of exact so that we can account for lineapy.api.api kind of names
        if our_name is not None:
            return our_name.startswith(name_to_compare)
        return self.compare_names(our_name, name_to_compare)


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

    def avisit(self, node):
        """Visit an argument node."""
        method = "argvisit_" + node.__class__.__name__
        visitor = getattr(self, method, self.lgeneric_visit)
        return visitor(node)

    def visit_Call(
        self, node: ast.Call
    ) -> Union[None, ast.Call, LineaCallNode]:
        func = self.lvisit(node.func)
        if (
            func is not None
            and isinstance(func, FunctionObj)
            and func.check_module_name(LINEA_ENDPOINTS.LINEAPY.value)
        ):
            args_to_pass = []
            to_exec = healthcheck
            artifact_name: Optional[str] = None
            argument_values = [self.avisit(arg) for arg in node.args]
            dependent = []
            # keyword_values = {key:value for }
            if func.check_function_name(
                LINEA_ENDPOINTS.SAVE.value
            ):  # func[1] == "save":
                artifact_name = argument_values[
                    1
                ]  # .get_function_name()  # argument_values[1]
                # this is to locate this node in the graph. its predecessors
                # are the var we are trying to save as an artifact
                # there can only be one - for now
                reference = argument_values[0]
                if isinstance(reference, FunctionObj):
                    # if this happens the artifact you are trying to save is a lineapy function/var like external state etc.
                    # in that case, we pick the actual attribute.
                    arg = reference.func  # argument_values[0][3]
                    argnode = self.tracer.executor._value_to_node[arg]
                else:
                    argnode = self.tracer.lookup_node(reference, None).id
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
                to_exec = LINEA_ENDPOINT_MAPPING[LINEA_ENDPOINTS.SAVE]  # type: ignore
            if func.check_function_name(
                LINEA_ENDPOINTS.GET.value
            ):  # func[1] == "get":
                artifact_name = argument_values[0]
                args_to_pass = [artifact_name]
                to_exec = _get  # type: ignore

            if func.check_function_name(
                LINEA_ENDPOINTS.ARTIFACT_STORE.value
            ):  # func[1] == "artifact_store":
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
                module_name=func.get_module_name(),
                function_name=func.get_function_name(),
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

    def lvisit_Attribute(self, node: ast.Attribute) -> Optional[FunctionObj]:
        value = self.avisit(node.value)
        if value is None:
            return None
        # if the module is in our imports list - because we only care about lineapy,
        # we will simply bother with this dict and ignore others
        module_imported: Optional[ModuleType] = None
        if value in self.tracer.module_name_to_node:
            module_imported = self.tracer.executor.get_value(  # type: ignore
                self.tracer.module_name_to_node[value].id
            )
        elif value in self.tracer.variable_name_to_node:
            print("module might be alias")
            # TODO - check if module type
            module_imported = self.tracer.executor.get_value(  # type: ignore
                self.tracer.variable_name_to_node[value].id
            )

        if module_imported is not None and hasattr(
            module_imported, "__name__"
        ):
            # module_name = module_imported.__name__
            attribute = getattr(module_imported, node.attr)
            # attribute_name = attribute.__name__
            retobj = FunctionObj(module_imported.__name__, attribute)
            # return (module_name, attribute_name, module_imported, attribute)
            return retobj

        return None

    def lvisit_Name(self, node: ast.Name) -> Optional[FunctionObj]:
        # return node.id
        if node.id not in self.tracer.variable_name_to_node:
            return None
        function_or_module = self.tracer.executor.get_value(
            self.tracer.variable_name_to_node[node.id].id
        )
        if hasattr(function_or_module, "__module__"):
            return FunctionObj(
                function_or_module.__module__, function_or_module
            )
            # return function_or_module.__name__
        return None

    def argvisit_Attribute(self, node: ast.Attribute) -> Optional[FunctionObj]:
        if node.value not in self.tracer.variable_name_to_node:
            return self.lvisit_Attribute(node)
        val = self.tracer.executor.get_value(  # type: ignore
            self.tracer.variable_name_to_node[node.value].id
        )
        return getattr(val, node.attr)
        # return self.lvisit_Attribute(node)

    def argvisit_Name(self, node):
        return node.id

    def argvisit_Constant(self, node):
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
