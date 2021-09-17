import builtins
import importlib.util
import io
from lineapy.utils import CaseNotHandledError, InternalLogicError
import subprocess
import sys
from typing import Any, Tuple, Optional, Dict, cast
import time

import lineapy.lineabuiltins as lineabuiltins
from lineapy.data.graph import Graph
from lineapy.data.types import (
    SessionContext,
    NodeType,
    Node,
    CallNode,
    ImportNode,
    LiteralNode,
    SideEffectsNode,
    StateChangeNode,
    FunctionDefinitionNode,
    LineaID,
    VariableNode,
)
from lineapy.execution.code_util import get_segment_from_code
from lineapy.graph_reader.base import GraphReader


class Executor(GraphReader):
    def __init__(self):
        self._variable_values = {}

        # Note: no output will be shown in Terminal because it is being redirected here
        self._old_stdout = sys.stdout
        self._stdout = io.StringIO()

    # TODO when we implement caching
    # @property
    # def data_asset_manager(self) -> DataAssetManager:
    #     pass

    @staticmethod
    def install(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    @staticmethod
    def lookup_module(module_node: Optional[Node], fn_name: str) -> Optional[Any]:
        if hasattr(lineabuiltins, fn_name):
            return lineabuiltins

        if module_node is None:
            return builtins

        if module_node.node_type == NodeType.ImportNode:
            module_node = cast(ImportNode, module_node)
            if module_node.module is None:
                module_node.module = importlib.import_module(module_node.library.name)  # type: ignore
            return module_node.module

        return None

    def setup(self, context: SessionContext) -> None:
        """
        Set up the execution environment by installing the necessary libraries.

        :param context: `SessionContext` including the necessary libraries.
        """
        if context.libraries is not None:
            for library in context.libraries:
                try:
                    if importlib.util.find_spec(library.name) is None:
                        Executor.install(library.name)
                except ModuleNotFoundError:
                    # Note: look out for errors when handling imports with multiple levels of parent packages (e.g. from x.y.z import a)
                    Executor.install(library.name.split(".")[0])

    def get_stdout(self) -> str:
        """
        This returns the text that corresponds to the stdout results.
        For instance, `print("hi")` should yield a result of "hi\n" from this function.

        Note:
        - If we assume that everything is sliced, the user printing may not happen, but third party libs may still have outputs.
        - Also the user may manually annotate for the print line to be included and in general stdouts are useful
        """

        val = self._stdout.getvalue()
        return val

    def get_value_by_variable_name(self, name: str) -> Any:
        if name in self._variable_values:
            return self._variable_values[name]
        else:
            # throwing internal logic error because this is only called
            #   for testing right now
            raise InternalLogicError(f"Cannot find variable {name}")

    def execute_program_with_inputs(
        self, program: Graph, inputs: Dict[LineaID, Any]
    ) -> Any:
        """
        Execute the `program` with specific `inputs`.
        Note: the inputs do not have to be root nodes in `program`. For a non-root node input, we should cut its
        dependencies. For example `a = foo(), b = a + 1`, if `a` is passed in as an input with value `2`, we should
        skip `foo()`.

        TODO:
        :param program: program to be run.
        :param inputs: mapping for node id to values for a set of input nodes.
        :return: result of the program run with specified inputs.
        """
        ...

    def execute_program(self, program: Graph, context: SessionContext) -> float:
        if context is not None:
            self.setup(context)

        start = time.time()
        self.walk(program, context.code)
        end = time.time()
        return end - start

    def setup_context_for_node(
        self,
        node: SideEffectsNode,
        program: Graph,
        scoped_locals: Dict[str, Any],
    ) -> None:
        if node.input_state_change_nodes is not None:
            for state_var_id in node.input_state_change_nodes:
                state_var = cast(StateChangeNode, program.get_node(state_var_id))
                # if state_var.state_dependency_type is StateDependencyType.Read:
                initial_state = program.get_node(state_var.initial_value_node_id)
                if initial_state is not None and initial_state.node_type in [
                    NodeType.CallNode,
                    NodeType.LiteralNode,
                    NodeType.StateChangeNode,
                ]:
                    scoped_locals[state_var.variable_name] = initial_state.value  # type: ignore

        if node.import_nodes is not None:
            for import_node_id in node.import_nodes:
                import_node = cast(ImportNode, program.get_node(import_node_id))
                import_node.module = importlib.import_module(import_node.library.name)  # type: ignore
                scoped_locals[import_node.library.name] = import_node.module

    def update_node_side_effects(
        self,
        node: Optional[Node],
        program: Graph,
        scoped_locals: Dict[str, Any],
    ) -> None:
        if node is None:
            return

        local_vars = scoped_locals
        node = cast(SideEffectsNode, node)
        if node.output_state_change_nodes is not None:
            for state_var_id in node.output_state_change_nodes:
                state_var = cast(StateChangeNode, program.get_node(state_var_id))

                # if state_var.state_dependency_type is StateDependencyType.Write:
                state_var.value = local_vars[state_var.variable_name]

                if state_var.variable_name is not None:
                    self._variable_values[state_var.variable_name] = state_var.value

    @staticmethod
    def get_function(
        node: CallNode, program: Graph, scoped_locals: Dict[str, Any]
    ) -> Tuple[Any, str]:
        fn_name = node.function_name
        fn = None

        if node.locally_defined_function_id is not None:
            fn = scoped_locals[fn_name]
        else:
            function_module = program.get_node(node.function_module)
            if (
                function_module is not None
                and function_module.node_type == NodeType.ImportNode
            ):
                function_module = cast(ImportNode, function_module)
                if function_module.attributes is not None:
                    fn_name = function_module.attributes[node.function_name]

            retrieved_module = Executor.lookup_module(function_module, fn_name)

            # if we are performing a call on an object, e.g. a.append(5)
            if retrieved_module is None:
                retrieved_module = program.get_node_value(function_module)

            fn = getattr(retrieved_module, fn_name)

        return fn, fn_name

    def walk(self, program: Graph, code: str) -> None:
        sys.stdout = self._stdout

        for node_id in program.visit_order():
            node = program.get_node(node_id)
            if node is None:
                print(f"WARNING: Could not find node with ID {node_id}")
                continue

            scoped_locals = locals()

            # all of these have to be in the same scope in order to read
            # and write to scoped_locals properly using Python exec

            if node.node_type == NodeType.CallNode:
                node = cast(CallNode, node)
                fn, fn_name = Executor.get_function(node, program, scoped_locals)

                args = program.get_arguments_from_call_node(node)

                val = fn(*args)
                node.value = val

                # update the assigned variable
                if node.assigned_variable_name is not None:
                    self._variable_values[node.assigned_variable_name] = node.value

                # if we are calling a locally defined function
                if node.locally_defined_function_id is not None:
                    locally_defined_func = program.get_node(
                        node.locally_defined_function_id
                    )
                    self.update_node_side_effects(
                        locally_defined_func,
                        program,
                        scoped_locals,
                    )

            elif node.node_type == NodeType.ImportNode:
                node = cast(ImportNode, node)
                node.module = importlib.import_module(node.library.name)

            elif node.node_type in [NodeType.LoopNode, NodeType.ConditionNode]:
                node = cast(SideEffectsNode, node)
                # set up vars and imports
                self.setup_context_for_node(node, program, scoped_locals)
                exec(get_segment_from_code(code, node))
                self.update_node_side_effects(node, program, scoped_locals)

            elif node.node_type == NodeType.FunctionDefinitionNode:
                node = cast(FunctionDefinitionNode, node)
                self.setup_context_for_node(node, program, scoped_locals)
                exec(
                    get_segment_from_code(code, node),
                    scoped_locals,
                )

            elif node.node_type == NodeType.LiteralNode:
                node = cast(LiteralNode, node)
                # no-op if it's headless
                if node.assigned_variable_name is not None:
                    self._variable_values[node.assigned_variable_name] = node.value

            elif node.node_type == NodeType.VariableNode:
                node = cast(VariableNode, node)
                if node.assigned_variable_name is not None:
                    node.value = program.get_node_value_from_id(node.source_variable_id)
                    self._variable_values[node.assigned_variable_name] = node.value

            # not all node cases are handled, including
            # - DataSourceNode
            # - ArgumentNode

        sys.stdout = self._old_stdout

    def validate(self, program: Graph) -> None:
        raise NotImplementedError("validate is not implemented!")
