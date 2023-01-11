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
    object to runnable code components, including code to define and run the NodeCollection defined subgraphs
    as well as the Session as a whole.

    Terminology

    Take the following example function and the line to call it:

    ``` python

        def function_name(input_parameters):
            code_line_1
            code_line_2
            return return_values

        function_name(input_parameters)
    ```

    We define the code block

    ``` python

        code_line_1
        code_line_2
        return return_values
    ```

    as the function body.

    The code block that calls the function

    ``` python

        function_name(input_parameters)
    ```

    is called the function call block.
    """

    def __init__(self):
        pass

    def get_session_module_imports(
        self,
        session_artifact: SessionArtifacts,
    ) -> str:
        """
        Return all the import statement for the session.
        """

        return session_artifact.import_nodecollection.get_import_block(
            graph=session_artifact.graph,
        )

    def get_session_function_name(
        self, session_artifact: SessionArtifacts
    ) -> str:
        """
        Return the session function name: run_session_including_{first_artifact_name}
        """
        first_artifact_name = session_artifact._get_first_artifact_name()
        if first_artifact_name is not None:
            return f"run_session_including_{first_artifact_name}"
        return ""

    def get_session_artifact_functions(
        self,
        session_artifact: SessionArtifacts,
        include_non_slice_as_comment=False,
    ) -> List[str]:
        """
        Return the function definition of the NodeCollection subgraphs that make up the Session.
        """
        return [
            coll.get_function_definition(
                graph=session_artifact.session_graph,
                include_non_slice_as_comment=include_non_slice_as_comment,
            )
            for coll in session_artifact.usercode_nodecollections
        ]

    def get_session_artifact_function_call_block(
        self,
        coll: UserCodeNodeCollection,
        keep_lineapy_save=False,
        return_dict_name=None,
        source_module="",
    ) -> str:
        """
        Return a codeblock to call the function that returns various variables.

        The actual function to produce the output variables is implemented in `get_function_definition`
        by the various implementations of NodeCollection.

        Parameters
        ----------
        coll: UserCodeNodeCollection
            the NodeCollection subgraph that we want to produce a call block for.
        keep_lineapy_save: bool
            whether do lineapy.save() after execution
        result_placeholder: Optional[str]
            if not null, append the return result to the result_placeholder
        source_module: str
            which module the function is coming from

        Example output:

        ``` python

            p = get_multiplier()                        # function call block that calculates multiplier
            lineapy.save(p, "multiplier")               # only with keep_lineapy_save=True
            artifacts["multiplier"]=copy.deepcopy(p)    # only with return_dict_name specified
        ```

        The result_placeholder is a list to capture the artifact variables right
        after calculation. Considering following code:

        ``` python

            a = 1
            lineapy.save(a,'a')
            a+=1
            b = a+1
            lineapy.save(b,'b')
            c = a+1
            lineapy.save(c,'c')
        ```
        we need to record the artifact a before it is mutated.
        """

        return_string = ", ".join(coll.return_variables)
        args_string = ", ".join(sorted([v for v in coll.input_variables]))
        if isinstance(coll, ArtifactNodeCollection) and coll.is_pre_computed:
            args_string = ""

        # handle calling the function from a module
        if source_module != "":
            source_module = f"{source_module}."
        codeblock = f"{return_string} = {source_module}get_{coll.safename}({args_string})"
        if keep_lineapy_save and isinstance(coll, ArtifactNodeCollection):
            codeblock += f"""\nlineapy.save({coll.return_variables[0]}, "{coll.name}")"""

        if (
            isinstance(coll, ArtifactNodeCollection)
            and return_dict_name is not None
        ):
            codeblock += f"""\n{return_dict_name}["{coll.name}"]=copy.deepcopy({coll.return_variables[0]})"""

        return codeblock

    def get_session_function_body(
        self,
        session_artifact: SessionArtifacts,
        return_dict_name="artifacts",
    ) -> str:
        """
        Return a codeblock that runs functions needed to reproduce a session.

        This codeblock uses `get_function_call_block` to call all of the functions defined by
        NodeCollections in the session specified bt `session_artifact`.
        The result codeblock can be used as the body of function that runs all the code in a session.

        Example output:

        ``` python

            # Session contains artifacts for "multiplier" and "prod_p"
            p = get_multiplier()
            artifacts["multiplier"]=copy.deepcopy(p)
            b = get_prod_p(a, p)
            artifacts["prod_p"]=copy.deepcopy(b)
        ```

        All artifacts in the session are saved in the return dictionary `artifacts`
        """
        return "\n".join(
            [
                self.get_session_artifact_function_call_block(
                    coll,
                    keep_lineapy_save=False,
                    return_dict_name=return_dict_name,
                )
                for coll in session_artifact.usercode_nodecollections
            ]
        )

    def get_session_input_parameters_lines(
        self,
        session_artifact: SessionArtifacts,
        indentation=4,
    ) -> str:
        """
        get_session_input_parameters_lines returns lines of session code
        that are replaced by user selected `input_parameters`.
        These lines also serve as the default values of these variables.

        Example output:

        ``` python

            # User called lineapy api with input_parameters=['a', 'p']
            a = 1,
            p = 2,
        ```

        """
        return session_artifact.input_parameters_nodecollection.get_input_parameters_block(
            graph=session_artifact.graph,
            indentation=indentation,
        )

    def get_session_input_parameters_spec(
        self, session_artifact
    ) -> Dict[str, InputVariable]:
        """
        get_session_input_parameters_spec returns a `session_input_variables` dictionary,
        which maps a key corresponding to the argument name to Linea's InputVariable
        object for each input parameter to a Session.

        Resulting InputVariable can be serialized by frameworks that may require non-pythonic
        format where the raw code lines are insufficient.
        """
        session_input_variables: Dict[str, InputVariable] = dict()
        # Create a new mapping to InputVariable for each input parameter line
        for line in self.get_session_input_parameters_lines(
            session_artifact
        ).split("\n"):
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

    def get_session_function(
        self,
        session_artifact,
        return_dict_name="artifacts",
    ) -> str:
        """
        Return the session function that executes the
        calculation of all targeted artifacts.

        Example output:

        ``` python

            def run_session_including_multiplier(
                a=1,
                p=2,
            ):
                artifacts = dict()
                p = get_multiplier()
                artifacts["multiplier"] = copy.deepcopy(p)
                b = get_prod_p(a, p)
                artifacts["prod_p"] = copy.deepcopy(b)
                return artifacts
        ```
        """
        SESSION_FUNCTION_TEMPLATE = load_plugin_template(
            "module/session_function.jinja"
        )
        session_function = SESSION_FUNCTION_TEMPLATE.render(
            session_input_parameters_body=self.get_session_input_parameters_lines(
                session_artifact=session_artifact,
            ),
            session_function_name=self.get_session_function_name(
                session_artifact=session_artifact,
            ),
            session_function_body=self.get_session_function_body(
                session_artifact=session_artifact,
            ),
            return_dict_name=return_dict_name,
        )
        return session_function

    def get_session_function_callblock(
        self,
        session_artifact: SessionArtifacts,
    ) -> str:
        """
        `get_session_function_callblock` returns the code to make the call to the session function.

        Example output:

        ``` python

            run_session_including_multiplier(a, p)
        ```
        """

        session_function_name = self.get_session_function_name(
            session_artifact
        )
        if session_function_name != "":
            session_input_parameters = ", ".join(
                self.get_session_input_parameters_spec(session_artifact).keys()
            )
            return f"{session_function_name}({session_input_parameters})"
        else:
            return ""
