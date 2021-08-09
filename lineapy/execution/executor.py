from abc import abstractmethod
from typing import Any
import io
import sys

from lineapy.data.graph import Graph
from lineapy.data.types import SessionContext, NodeType
from lineapy.db.asset_manager.base import DataAssetManager
from lineapy.graph_reader.base import GraphReader


class Executor(GraphReader):

    @property
    def data_asset_manager(self) -> DataAssetManager:
        pass

    def setup(self, context: SessionContext) -> None:
        """
        TODO set up the execution environment based on `context`
        """
        pass

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

    def get_value_by_varable_name(self, name: str) -> Any:
        return self._variable_values[name]

    def walk(self, program: Graph) -> None:
        self._variable_values = {}

        # Note: no output will be shown in Terminal because it is being redirected here
        self._oldstdout = sys.stdout
        self._stdout = io.StringIO()
        sys.stdout = self._stdout

        for node_id in program.top_sort():
            node = program.get_node(node_id)
            
            if node.node_type == NodeType.CallNode:
                string_args = []
                for arg in node.arguments:
                    if arg.value_literal:
                        string_args.append(str(arg.value_literal))
                    elif arg.value_call_id:
                        string_args.append(str(program.get_node(arg.value_call_id).value))
                val = eval('%s(%s)' % (node.function_name, ', '.join(string_args)))
                
                node.value = val
                if node.assigned_variable_name:
                    self._variable_values[node.assigned_variable_name] = node.value
            
            elif node.node_type == NodeType.ImportNode:
                import_code = ""
                if node.attributes:
                    attributes = []
                    for attr in node.attributes:
                        if attr[1]:
                            attributes.append("%s as %s" % (attr[0], attr[1]))
                        else:
                            attributes.append(attr[0])
                    import_code = "from %s import %s" % (node.library.name, ', '.join(attributes))
                else:
                    import_code = "import %s" % node.library.name
                    if node.alias:
                        import_code = "%s as %s" % (import_code, node.alias)
                exec(import_code)

        sys.stdout = self._oldstdout
