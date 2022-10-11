import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from lineapy.api.models.linea_artifact import LineaArtifactDef
from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.graph_reader.program_slice import get_source_code_from_graph
from lineapy.plugins.utils import slugify
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


@dataclass
class BaseNodeCollection:
    """
    BaseNodeCollection represents a collection of Nodes in a Graph.

    Used for defining modules and functions.
    """

    node_list: Set[LineaID]
    graph: Graph
    name: str

    def __post_init__(self):
        self.safename = slugify(self.name)

    def _get_graph_segment(self) -> Graph:
        return self.graph.get_subgraph_from_id(list(self.node_list))

    def _get_raw_codeblock(self, include_non_slice_as_comment=False) -> str:
        graph_segment = self._get_graph_segment()
        return get_source_code_from_graph(
            graph_segment, include_non_slice_as_comment
        ).__str__()


@dataclass
class UserCodeNodeCollection(BaseNodeCollection):
    """
    This class is used for holding a set of node(as a subgraph)
    corresponding to user code that can be sliced on.

    It is initiated with list of nodes::

        seg = NodeCollection(node_list)

    For variable calculation calculation purpose, it can identify all variables
    related to these by running::

        seg._update_variable_info()

    For all code generating purpose, it need to initiate a real graph objects by::

        seg.update_raw_codeblock()
    """

    assigned_variables: Set[str] = field(default_factory=set)
    dependent_variables: Set[str] = field(default_factory=set)
    all_variables: Set[str] = field(default_factory=set)
    input_variables: Set[str] = field(default_factory=set)
    tracked_variables: Set[str] = field(default_factory=set)
    predecessor_nodes: Set[LineaID] = field(default_factory=set)
    # Need to be a list to keep return order
    return_variables: List[str] = field(default_factory=list)

    def get_input_variable_sources(self, node_context) -> Dict[str, Set[str]]:
        """
        Get information about which input variable is originated from which artifact.
        """
        input_variable_sources: Dict[str, Set[str]] = dict()
        for pred_id in self.predecessor_nodes:
            pred_variables = (
                node_context[pred_id].assigned_variables
                if len(node_context[pred_id].assigned_variables) > 0
                else node_context[pred_id].tracked_variables
            )
            pred_art = node_context[pred_id].artifact_name
            assert isinstance(pred_art, str)
            if pred_art != "module_import":
                input_variable_sources[pred_art] = input_variable_sources.get(
                    pred_art, set()
                ).union(pred_variables)
        return input_variable_sources

    def update_variable_info(self, node_context, input_parameters_node):
        """
        Update variable information to add user defined input parameters.
        """
        self.dependent_variables = self.dependent_variables.union(
            *[node_context[nid].dependent_variables for nid in self.node_list]
        )
        # variables got assigned within these nodes
        self.assigned_variables = self.assigned_variables.union(
            *[node_context[nid].assigned_variables for nid in self.node_list]
        )
        # all variables within these nodes
        self.all_variables = self.dependent_variables.union(
            self.assigned_variables
        ).union(set(self.return_variables))
        # required input variables
        self.input_variables = self.all_variables - self.assigned_variables
        # Add user defined parameter in to input variables list
        user_input_parameters = set(
            [
                var
                for var, nid in input_parameters_node.items()
                if nid in self.node_list
            ]
        )
        self.input_variables = self.input_variables.union(
            user_input_parameters
        )

    def get_function_definition(self, indentation=4) -> str:
        """
        Return a codeblock to define the function of the graph segment.
        """
        indentation_block = " " * indentation
        name = self.safename
        return_string = ", ".join([v for v in self.return_variables])

        artifact_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in self._get_raw_codeblock().split("\n")
                if len(line.strip(" ")) > 0
            ]
        )
        args_string = ", ".join(sorted([v for v in self.input_variables]))

        return f"def get_{name}({args_string}):\n{artifact_codeblock}\n{indentation_block}return {return_string}"


@dataclass
class ArtifactNodeCollection(UserCodeNodeCollection):
    """
    ArtifactNodeCollection is a special subclass of UserCodeNodeCollection which return Artifacts.

    If is_pre_computed is True, this means that this NodeCollection should use a precomputed
    Artifact's value.
    """

    is_pre_computed: bool = False
    pre_computed_artifact: Optional[LineaArtifactDef] = None

    def get_function_definition(self, indentation=4) -> str:
        """
        Return a codeblock to define the function of the graph segment.

        If self.is_pre_computed_artifact is True, will replace the calculation
        block with lineapy.get().get_value()
        """

        if not self.is_pre_computed:
            return super().get_function_definition(indentation)
        else:
            assert self.pre_computed_artifact is not None
            indentation_block = " " * indentation
            name = self.safename
            return_string = ", ".join([v for v in self.return_variables])
            artifact_codeblock = (
                f"{indentation_block}import lineapy\n{indentation_block}"
            )
            artifact_codeblock += f'{return_string}=lineapy.get("{self.pre_computed_artifact["artifact_name"]}", {self.pre_computed_artifact["version"]}).get_value()'
            args_string = ""

            return f"def get_{name}({args_string}):\n{artifact_codeblock}\n{indentation_block}return {return_string}"


class ImportNodeCollection(BaseNodeCollection):
    """
    ImportNodeCollection contains all the nodes used to import libraries in a Session.
    """

    def get_import_block(self, indentation=0) -> str:
        """
        Return a code block for import statement of the graph segment
        """
        raw_codeblock = self._get_raw_codeblock()
        if raw_codeblock == "":
            return ""

        indentation_block = " " * indentation
        import_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in raw_codeblock.split("\n")
                if len(line.strip(" ")) > 0
            ]
        )
        if len(import_codeblock) > 0:
            import_codeblock += "\n" * 2
        return import_codeblock


class InputVarNodeCollection(BaseNodeCollection):
    """
    InputVarNodeCollection contains all the nodes that are needed as input parameters
    to the Session.
    """

    def get_input_parameters_block(self, indentation=4) -> str:
        """
        Return a code block for input parameters of the graph segment
        """
        raw_codeblock = self._get_raw_codeblock()
        if raw_codeblock == "":
            return ""

        indentation_block = " " * indentation
        input_parameters_lines = raw_codeblock.rstrip("\n").split("\n")

        if len(input_parameters_lines) > 1:
            input_parameters_codeblock = "\n" + "".join(
                [
                    f"{indentation_block}{line},\n"
                    for line in input_parameters_lines
                ]
            )
        elif len(input_parameters_lines) == 1:
            input_parameters_codeblock = input_parameters_lines[0]
        else:
            input_parameters_codeblock = ""

        return input_parameters_codeblock


@dataclass
class NodeInfo:
    """
    :assigned_variables: variables assigned at this node
    :assigned_artifact: this node is pointing to some artifact
    :dependent_variables: union of if any variable is assigned at predecessor node,
     use the assigned variables. otherwise, use the dependent_variables
    :tracked_variables: variables that this node is point to
    :predecessors: predecessors of the node
    :module_import: module name/alias that this node is point to
    :artifact_name: this node belong to which artifact calculating block
    """

    assigned_variables: Set[str] = field(default_factory=set)
    assigned_artifact: Optional[str] = field(default=None)
    dependent_variables: Set[str] = field(default_factory=set)
    predecessors: Set[LineaID] = field(default_factory=set)
    tracked_variables: Set[str] = field(default_factory=set)
    module_import: Set[str] = field(default_factory=set)
    artifact_name: Optional[str] = field(default=None)
