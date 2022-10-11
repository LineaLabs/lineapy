from typing import Dict, List

from lineapy.graph_reader.node_collection import (
    ArtifactNodeCollection,
    UserCodeNodeCollection,
)
from lineapy.graph_reader.session_artifacts import SessionArtifacts
from lineapy.graph_reader.types import InputVariable
from lineapy.plugins.utils import load_plugin_template


class BaseSessionWriter:
    """
    BaseSessionWriter contains helper functions to turn the various components of a SessionArtifacts
    object to runnable code.
    """

    def __init__(self, session_artifact: SessionArtifacts):
        self.session_artifact = session_artifact

    def get_session_module_imports(self, indentation=0) -> str:
        """
        Return all the import statement for the session.
        """
        return self.session_artifact.import_nodecollection.get_import_block(
            indentation=indentation
        )

    def get_session_function_name(self) -> str:
        """
        Return the session function name: run_session_including_{first_artifact_name}
        """
        first_artifact_name = self.session_artifact._get_first_artifact_name()
        if first_artifact_name is not None:
            return f"run_session_including_{first_artifact_name}"
        return ""

    def get_function_call_block(
        self,
        coll: UserCodeNodeCollection,
        indentation=0,
        keep_lineapy_save=False,
        return_dict_name=None,
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
        return_string = ", ".join(coll.return_variables)
        args_string = ", ".join(sorted([v for v in coll.input_variables]))
        if isinstance(coll, ArtifactNodeCollection) and coll.is_pre_computed:
            args_string = ""

        # handle calling the function from a module
        if source_module != "":
            source_module = f"{source_module}."
        codeblock = f"{indentation_block}{return_string} = {source_module}get_{coll.safename}({args_string})"
        if keep_lineapy_save and isinstance(coll, ArtifactNodeCollection):
            codeblock += f"""\n{indentation_block}lineapy.save({coll.return_variables[0]}, "{coll.name}")"""

        if (
            isinstance(coll, ArtifactNodeCollection)
            and return_dict_name is not None
        ):
            codeblock += f"""\n{indentation_block}{return_dict_name}["{coll.name}"]=copy.deepcopy({coll.return_variables[0]})"""

        return codeblock

    def get_session_function_body(
        self, indentation, return_dict_name="artifacts"
    ) -> str:
        """
        Return the args for the session function.
        """
        return "\n".join(
            [
                self.get_function_call_block(
                    coll,
                    indentation=indentation,
                    keep_lineapy_save=False,
                    return_dict_name=return_dict_name,
                )
                for coll in self.session_artifact.artifact_nodecollections
            ]
        )

    def _get_session_input_parameters_lines(self, indentation=4) -> str:
        """
        Return lines of session code that are replaced by user selected input
        parameters. These lines also serve as the default values of these
        variables.
        """
        return self.session_artifact.input_parameters_nodecollection.get_input_parameters_block(
            indentation=indentation
        )

    def get_session_input_parameters_spec(self) -> Dict[str, InputVariable]:
        """
        Return a dictionary with input parameters as key and InputVariable
        class as value to generate code related to user input variables.
        """
        session_input_variables: Dict[str, InputVariable] = dict()
        for line in self._get_session_input_parameters_lines().split("\n"):
            variable_def = line.strip(" ").rstrip(",")
            if len(variable_def) > 0:
                variable_name = variable_def.split("=")[0].strip(" ")
                value = eval(variable_def.split("=")[1].strip(" "))
                value_type = type(value)
                if not (
                    isinstance(value, int)
                    or isinstance(value, float)
                    or isinstance(value, str)
                    or isinstance(value, bool)
                ):
                    raise ValueError(
                        f"LineaPy only supports primitive types as input parameters for now. "
                        f"{variable_name} in {variable_def} is a {value_type}."
                    )
                if ":" in variable_name:
                    variable_name = variable_def.split(":")[0]
                    session_input_variables[variable_name] = InputVariable(
                        variable_name=variable_name,
                        value=value,
                        value_type=value_type,
                    )
                else:
                    session_input_variables[variable_name] = InputVariable(
                        variable_name=variable_name,
                        value=value,
                        value_type=value_type,
                    )
        return session_input_variables

    def get_session_function_callblock(self) -> str:
        """
        Return the code to make the call to the session function as
        `session_function_name(input_parameters)`.
        """
        session_function_name = self.get_session_function_name()
        if session_function_name != "":
            session_input_parameters = ", ".join(
                self.get_session_input_parameters_spec().keys()
            )
            return f"{session_function_name}({session_input_parameters})"
        else:
            return ""

    def get_session_artifact_function_definitions(
        self, indentation=4
    ) -> List[str]:
        """
        Return the definition of each targeted artifacts calculation
        functions.
        """
        return [
            coll.get_function_definition(indentation=indentation)
            for coll in self.session_artifact.artifact_nodecollections
        ]

    def get_session_function(
        self, indentation=4, return_dict_name="artifacts"
    ) -> str:
        """
        Return the definition of the session function that executes the
        calculation of all targeted artifacts.
        """
        indentation_block = " " * indentation
        SESSION_FUNCTION_TEMPLATE = load_plugin_template(
            "session_function.jinja"
        )
        session_function = SESSION_FUNCTION_TEMPLATE.render(
            session_input_parameters_body=self._get_session_input_parameters_lines(),
            indentation_block=indentation_block,
            session_function_name=self.get_session_function_name(),
            session_function_body=self.get_session_function_body(
                indentation=indentation
            ),
            return_dict_name=return_dict_name,
        )
        return session_function
