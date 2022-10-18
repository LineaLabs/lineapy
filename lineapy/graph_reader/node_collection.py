import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

from lineapy.data.graph import Graph
from lineapy.data.types import LineaID
from lineapy.graph_reader.program_slice import get_source_code_from_graph
from lineapy.plugins.utils import slugify
from lineapy.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


class NodeCollectionType(Enum):
    """
    NodeCollection type to identify the purpose of the node collection

    :ARTIFACT: node collection for artifact calculation
    :COMMON_VARIABLE: node collection for calculating variables used in multiple artifacts
    :IMPORT: node collection for module import
    :INPUT_VARIABLE: node collection for input variables
    """

    ARTIFACT = 1
    COMMON_VARIABLE = 2
    IMPORT = 3
    INPUT_PARAMETERS = 4


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


@dataclass
class NodeCollection:
    """
    This class is used for holding a set of node(as a subgraph) with same purpose;
    for instance, calculating some variables, module import, variable assignments.
    It is initiated with list of nodes::

        seg = NodeCollection(node_list)

    For variable calculation calculation purpose, it can identify all variables
    related to these by running::

        seg._update_variable_info()

    For all code generating purpose, it need to initiate a real graph objects by::

        seg.update_raw_codeblock()

    Then, it provide following method to generat different codeblock for different
    purpose.
    """

    collection_type: NodeCollectionType
    node_list: Set[LineaID]

    name: str = field(default="")

    assigned_variables: Set[str] = field(default_factory=set)
    dependent_variables: Set[str] = field(default_factory=set)
    all_variables: Set[str] = field(default_factory=set)
    input_variables: Set[str] = field(default_factory=set)
    tracked_variables: Set[str] = field(default_factory=set)
    # Need to be a list to keep return order
    return_variables: List[str] = field(default_factory=list)

    artifact_node_id: Optional[LineaID] = field(default=None)
    predecessor_nodes: Set[LineaID] = field(default_factory=set)
    predecessor_artifact: Set[str] = field(default_factory=set)
    input_variable_sources: Dict[str, Set[str]] = field(default_factory=dict)
    safename: str = field(default="")
    graph_segment: Optional[Graph] = field(default=None)
    sliced_nodes: Set[LineaID] = field(default_factory=set)
    raw_codeblock: str = field(default="")
    is_empty: bool = field(default=True)
    pre_computed_artifact: Union[None, Tuple[str, Optional[int]]] = field(
        default=None
    )
    is_pre_computed_artifact: bool = field(default=False)

    def __post_init__(self):
        self.safename = slugify(self.name)
        self.is_pre_computed_artifact = self.pre_computed_artifact is not None

    def _update_variable_info(self, node_context, input_parameters_node):
        """
        Update variable information based on node_list
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

    def update_raw_codeblock(
        self, graph: Graph, include_non_slice_as_comment=False
    ) -> None:
        """
        Update graph_segment class member based on node_list

        Need to manually run this function at least once if you need the graph
        object for code generation.
        """
        self.graph_segment = graph.get_subgraph_from_id(list(self.node_list))
        self.raw_codeblock = get_source_code_from_graph(
            self.node_list, graph, include_non_slice_as_comment
        ).__str__()
        self.is_empty = self.raw_codeblock == ""

    def get_function_definition(self, indentation=4) -> str:
        """
        Return a codeblock to define the function of the graph segment. If
        self.is_pre_computed_artifact is True, will replace the calculation
        block with lineapy.get().get_value()
        """

        indentation_block = " " * indentation
        name = self.safename
        return_string = ", ".join([v for v in self.return_variables])
        if not self.is_pre_computed_artifact:
            artifact_codeblock = "\n".join(
                [
                    f"{indentation_block}{line}"
                    for line in self.raw_codeblock.split("\n")
                    if len(line.strip(" ")) > 0
                ]
            )
            args_string = ", ".join(sorted([v for v in self.input_variables]))
        else:
            assert self.pre_computed_artifact is not None
            artifact_codeblock = (
                f"{indentation_block}import lineapy\n{indentation_block}"
            )
            artifact_codeblock += f'{return_string}=lineapy.get("{self.pre_computed_artifact[0]}", {self.pre_computed_artifact[1]}).get_value()'
            args_string = ""

        return f"def get_{name}({args_string}):\n{artifact_codeblock}\n{indentation_block}return {return_string}"

    def get_function_call_block(
        self,
        indentation=0,
        keep_lineapy_save=False,
        result_placeholder=None,
        source_module="",
    ) -> str:
        """
        Return a codeblock to call the function with return variables of the graph segment

        :param int indentation: indentation size
        :param bool keep_lineapy_save: whether do lineapy.save() after execution
        :param Optional[str] result_placeholder: if not null, append the return result to the result_placeholder
        :param str source_module: which module the function is coming from

        The result_placeholder is a list to capture the artifact variables right
        after calculation. Considering following code::

            a = 1
            lineapy.save(a,'a')
            a+=1
            b = a+1
            lineapy.save(b,'b')
            c = a+1
            lineapy.save(c,'c')


        we need to record the artifact a before it is mutated.

        """

        indentation_block = " " * indentation
        return_string = ", ".join(self.return_variables)
        args_string = ", ".join(sorted([v for v in self.input_variables]))
        if self.is_pre_computed_artifact:
            args_string = ""

        # handle calling the function from a module
        if source_module != "":
            source_module = f"{source_module}."
        codeblock = f"{indentation_block}{return_string} = {source_module}get_{self.safename}({args_string})"
        if (
            keep_lineapy_save
            and self.collection_type == NodeCollectionType.ARTIFACT
        ):
            codeblock += f"""\n{indentation_block}lineapy.save({self.return_variables[0]}, "{self.name}")"""
        if result_placeholder is not None:
            codeblock += f"""\n{indentation_block}{result_placeholder}["{self.name}"]=copy.deepcopy({self.return_variables[0]})"""

        return codeblock

    def get_import_block(self, indentation=0) -> str:
        """
        Return a code block for import statement of the graph segment
        """
        if self.is_empty:
            return ""

        indentation_block = " " * indentation
        import_codeblock = "\n".join(
            [
                f"{indentation_block}{line}"
                for line in self.raw_codeblock.split("\n")
                if len(line.strip(" ")) > 0
            ]
        )
        if len(import_codeblock) > 0:
            import_codeblock += "\n" * 2
        return import_codeblock

    def get_input_parameters_block(self, indentation=4) -> str:
        """
        Return a code block for input parameters of the graph segment
        """
        if self.is_empty:
            return ""

        indentation_block = " " * indentation
        input_parameters_lines = self.raw_codeblock.rstrip("\n").split("\n")

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

        if self.pre_computed_artifact is not None:
            logger.warning(
                "Variables "
                + ", ".join(self.input_variables)
                + f" are dummy variables since they are only used in the calculation of artifacts {self.name}."
                + "You can either edit the input_parameters or reuse_pre_computed parameters to remove this warning."
            )
            return ""

        return input_parameters_codeblock
