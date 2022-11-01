import itertools
import logging
import pickle
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Union

import networkx as nx

from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.graph_reader.node_collection import (
    ArtifactNodeCollection,
    UserCodeNodeCollection,
)
from lineapy.graph_reader.types import InputVariable
from lineapy.plugins.session_writers import BaseSessionWriter
from lineapy.plugins.task import (
    AirflowDagConfig,
    DVCDagConfig,
    TaskDefinition,
    TaskGraphEdge,
)
from lineapy.plugins.utils import (
    PIP_PACKAGE_NAMES,
    load_plugin_template,
    slugify,
)
from lineapy.utils.logging_config import configure_logging
from lineapy.utils.utils import get_system_python_version, prettify

logger = logging.getLogger(__name__)
configure_logging()


class BasePipelineWriter:
    """
    Pipeline writer uses modularized artifact code to generate
    and write out standard pipeline files, including Python modules,
    DAG script, and infra files (e.g., Dockerfile).

    Base class for pipeline file writer corresponds to "SCRIPT" framework.
    """

    def __init__(
        self,
        artifact_collection: ArtifactCollection,
        dependencies: TaskGraphEdge = {},
        keep_lineapy_save: bool = False,
        pipeline_name: str = "pipeline",
        output_dir: str = ".",
        generate_test: bool = False,
        dag_config: Optional[Union[AirflowDagConfig, DVCDagConfig]] = None,
        include_non_slice_as_comment: Optional[bool] = False,
    ) -> None:
        self.artifact_collection = artifact_collection
        self.keep_lineapy_save = keep_lineapy_save
        self.pipeline_name = slugify(pipeline_name)
        self.output_dir = Path(output_dir)
        self.generate_test = generate_test
        self.dag_config = dag_config or {}
        self.dependencies = dependencies
        self.include_non_slice_as_comment = include_non_slice_as_comment

        self.session_artifacts_sorted = (
            self.artifact_collection.sort_session_artifacts(
                dependencies=dependencies
            )
        )
        # Create output directory folder(s) if nonexistent
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Specify (sub-)directory name to store test artifact values
        self.test_artval_dirname = "sample_output"

    @property
    def docker_template_name(self) -> str:
        return "script_dockerfile.jinja"

    @property
    def docker_template_params(self) -> Dict[str, str]:
        return {
            "pipeline_name": self.pipeline_name,
            "python_version": get_system_python_version(),
        }

    def _write_module(self) -> None:
        """
        Write out module file containing refactored code.
        """
        module_text = self._compose_module(
            indentation=4,
        )
        file = self.output_dir / f"{self.pipeline_name}_module.py"
        file.write_text(prettify(module_text))
        logger.info(f"Generated module file: {file}")

    def _compose_module(
        self,
        indentation: int = 4,
        return_dict_name="artifacts",
    ) -> str:
        """
        Generate a Python module that calculates artifacts
        in the given artifact collection.
        """

        # Sort sessions topologically (applicable if artifacts come from multiple sessions)

        indentation_block = " " * indentation

        module_imports = "\n".join(
            [
                BaseSessionWriter().get_session_module_imports(sa)
                for sa in self.session_artifacts_sorted
            ]
        )

        artifact_function_definition = "\n".join(
            list(
                itertools.chain.from_iterable(
                    [
                        BaseSessionWriter().get_session_artifact_functions(
                            session_artifact=sa,
                            include_non_slice_as_comment=self.include_non_slice_as_comment,
                            indentation=indentation,
                        )
                        for sa in self.session_artifacts_sorted
                    ]
                )
            )
        )

        session_functions = "\n".join(
            [
                BaseSessionWriter().get_session_function(
                    session_artifact=sa,
                    indentation=indentation,
                )
                for sa in self.session_artifacts_sorted
            ]
        )

        module_function_body = "\n".join(
            [
                f"{indentation_block}{return_dict_name}.update({BaseSessionWriter().get_session_function_call_block(sa)})"
                for sa in self.session_artifacts_sorted
            ]
        )

        module_input_parameters: List[InputVariable] = []
        for sa in self.session_artifacts_sorted:
            module_input_parameters += list(
                BaseSessionWriter()
                .get_session_input_parameters_spec(sa)
                .values()
            )

        module_input_parameters_list = [
            param.variable_name for param in module_input_parameters
        ]
        if len(module_input_parameters_list) != len(
            set(module_input_parameters_list)
        ):
            raise ValueError(
                f"Duplicated input parameters {module_input_parameters_list} across multiple sessions"
            )
        elif set(module_input_parameters_list) != set(
            self.artifact_collection.input_parameters
        ):
            missing_parameters = set(
                self.artifact_collection.input_parameters
            ) - set(module_input_parameters_list)
            raise ValueError(
                f"Detected input parameters {module_input_parameters_list} do not agree with user input {self.artifact_collection.input_parameters}. "
                + f"The following variables do not have references in any session code: {missing_parameters}."
            )

        # Sort input parameter for the run_all in the module as the same order
        # of user's input parameter
        user_input_parameters_ordering = {
            var: i
            for i, var in enumerate(self.artifact_collection.input_parameters)
        }
        module_input_parameters.sort(
            key=lambda x: user_input_parameters_ordering[x.variable_name]
        )

        # Put all together to generate module text
        MODULE_TEMPLATE = load_plugin_template("module.jinja")
        module_text = MODULE_TEMPLATE.render(
            indentation_block=indentation_block,
            module_imports=module_imports,
            artifact_functions=artifact_function_definition,
            session_functions=session_functions,
            module_function_body=module_function_body,
            default_input_parameters=[
                param.default_args for param in module_input_parameters
            ],
            parser_input_parameters=[
                param.parser_args for param in module_input_parameters
            ],
            parser_blocks=[
                param.parser_body for param in module_input_parameters
            ],
        )

        return prettify(module_text)

    def _write_requirements(self) -> None:
        """
        Write out requirements file.
        """
        libraries = dict()
        for session_artifacts in self.session_artifacts_sorted:
            session_artifact_libs = session_artifacts.get_libraries()
            for lib in session_artifact_libs:
                if isinstance(lib.package_name, str):
                    lib_name = PIP_PACKAGE_NAMES.get(
                        lib.package_name, lib.package_name
                    )
                    libraries[lib_name] = lib.version
        lib_names_text = "\n".join(
            [
                lib if lib == "lineapy" else f"{lib}=={ver}"
                for lib, ver in libraries.items()
            ]
        )
        file = self.output_dir / f"{self.pipeline_name}_requirements.txt"
        file.write_text(lib_names_text)
        logger.info(f"Generated requirements file: {file}")

    def _store_artval_for_testing(self) -> None:
        """
        (Re-)Store artifact values as pickle files to serve as "ground truths"
        to compare against for equality evaluation of function outputs. The new
        pickle files are to bear corresponding artifact names.
        """
        # Create subdirectory if nonexistent
        dirpath = self.output_dir / self.test_artval_dirname
        dirpath.mkdir(exist_ok=True, parents=True)

        # Store each artifact value
        for sa in self.artifact_collection.session_artifacts.values():
            for art in sa.target_artifacts:
                filepath = dirpath / f"{slugify(art.name)}.pkl"
                artval = art.get_value()
                with filepath.open("wb") as fp:
                    pickle.dump(artval, fp)

    def _write_module_test_scaffold(self) -> None:
        """
        Write out test scaffold for refactored code in module file.
        The scaffold contains placeholders for testing each function
        in the module file and is meant to be fleshed out by the user
        to suit their needs. When run out of the box, it performs a naive
        form of equality evaluation for each function's output,
        which demands validation and customization by the user.
        """
        # Extract information about each function in the pipeline module.
        # This information is to be eventually passed into file template.
        # Fields starting with an underscore are not intended for direct use
        # in the template; they are meant to be used for deriving other fields.
        # For instance, if the module file contains the following functions:
        #
        # .. code-block:: python
        #
        #     def get_url1_for_artifact_iris_model_and_downstream():
        #         url1 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
        #         return url1
        #
        #     def get_iris_model(url1):
        #         train_df = pd.read_csv(url1)
        #         mod = LinearRegression()
        #         mod.fit(
        #             X=train_df[["petal.width"]],
        #             y=train_df["petal.length"],
        #         )
        #         return mod
        #
        # Then, for the function ``get_iris_model()``, we would have the following
        # ``function_metadata_dict`` entry:
        #
        # .. code-block:: python
        #
        #     {
        #         "iris_model": {
        #             "name": "get_iris_model",
        #             "input_variable_names": ["url1"],
        #             "return_variable_names": ["mod"],
        #             "output_name": "iris_model",
        #             "_output_type": ArtifactNodeCollection,
        #             "dependent_output_names": ["url1_for_artifact_iris_model_and_downstream"],
        #         }
        #     }
        #
        # As shown, "output" here denotes artifact(s) or common variable(s) that
        # the function generates.
        function_metadata_dict = OrderedDict(
            {
                node_collection.safename: {
                    "name": f"get_{node_collection.safename}",
                    "input_variable_names": sorted(
                        [v for v in node_collection.input_variables]
                    ),
                    "return_variable_names": node_collection.return_variables,
                    "output_name": node_collection.safename,
                    "_output_type": node_collection.__class__.__name__,
                    "dependent_output_names": nx.ancestors(
                        session_artifacts.nodecollection_dependencies.graph,
                        node_collection.safename,
                    ),
                }
                for session_artifacts in self.session_artifacts_sorted
                for node_collection in session_artifacts.usercode_nodecollections
            }
        )

        # For each function in the pipeline module, topologically order its
        # dependent outputs (i.e., artifacts and/or common variables that should be
        # calculated beforehand). Leverage the fact that ``function_metadata_dict``
        # is already topologically sorted.
        for function_metadata in function_metadata_dict.values():
            function_metadata["dependent_output_names"] = [
                output_name
                for output_name in function_metadata_dict.keys()
                if output_name in function_metadata["dependent_output_names"]
            ]

        # Identify common variables factored out by LineaPy to reduce
        # redundant compute (rather than stored by the user as artifacts),
        # e.g., ``url1`` in the example above.
        intermediate_output_names = [
            function_metadata["output_name"]
            for function_metadata in function_metadata_dict.values()
            if function_metadata["_output_type"]
            == UserCodeNodeCollection.__name__
        ]

        # Format other components to be passed into file template
        module_name = f"{self.pipeline_name}_module"
        test_class_name = f"Test{self.pipeline_name.title().replace('_', '')}"

        # Fill in file template and write it out
        MODULE_TEST_TEMPLATE = load_plugin_template("module_test.jinja")
        module_test_text = MODULE_TEST_TEMPLATE.render(
            MODULE_NAME=module_name,
            TEST_CLASS_NAME=test_class_name,
            TEST_ARTVAL_DIRNAME=self.test_artval_dirname,
            FUNCTION_METADATA_LIST=function_metadata_dict.values(),
            FUNCTION_METADATA_DICT=function_metadata_dict,
            INTERMEDIATE_OUTPUT_NAMES=intermediate_output_names,
        )
        file = self.output_dir / f"test_{self.pipeline_name}.py"
        file.write_text(prettify(module_test_text))
        logger.info(f"Generated test scaffold file: {file}")
        logger.warning(
            "Generated tests are provided as template/scaffold to start with only; "
            "please modify them to suit your testing needs. "
            "Also, tests may involve long compute and/or large storage, "
            "so please take care in running them."
        )

    def _create_test(self) -> None:
        if self.generate_test is True:
            self._write_module_test_scaffold()
            self._store_artval_for_testing()
        else:
            pass

    def _write_dag(self) -> None:
        """
        Write out framework-specific DAG file
        """
        pass  # SCRIPT framework does not need DAG file

    def _write_docker(self) -> None:
        """
        Write out Docker file.
        """
        DOCKERFILE_TEMPLATE = load_plugin_template(self.docker_template_name)
        dockerfile_text = DOCKERFILE_TEMPLATE.render(
            **self.docker_template_params
        )
        file = self.output_dir / f"{self.pipeline_name}_Dockerfile"
        file.write_text(dockerfile_text)
        logger.info(f"Generated Docker file: {file}")

    def write_pipeline_files(self) -> None:
        """
        Write out pipeline files.
        """
        self._write_module()
        self._write_requirements()
        self._write_dag()
        self._write_docker()
        self._create_test()

    def get_pipeline_args(self) -> Dict[str, InputVariable]:
        """
        get_pipeline_args returns the arguments that are required as inputs to the whole pipeline.

        Returns a `pipeline_args` dictionary, which maps a key corresponding to the argument name to
        Linea's InputVariable object.
        Specific framework implementations of PipelineWriters should serialize the InputVariable
        objects to match the format for pipeline arguments that is expected by that framework.
        """
        pipeline_args: Dict[str, InputVariable] = dict()
        for sa in self.session_artifacts_sorted:
            pipeline_args.update(
                BaseSessionWriter().get_session_input_parameters_spec(sa)
            )
        return pipeline_args

    def get_artifact_task_definitions(
        self,
    ) -> Dict[str, TaskDefinition]:
        """
        get_artifact_task_definitions returns a task definition for each artifact the pipeline produces.
        This may include tasks that produce common variables that were not initially defined as artifacts.

        Returns a `task_definitions` dictionary, which maps a key corresponding to the task name to
        Linea's TaskDefinition object.
        Specific framework implementations of PipelineWriters should serialize the TaskDefinition
        objects to match the format for pipeline arguments that is expected by that framework.
        """
        task_definitions: Dict[str, TaskDefinition] = dict()
        unused_input_parameters = set(
            self.artifact_collection.input_parameters
        )
        session_input_parameters_spec = self.get_pipeline_args()

        for session_artifacts in self.session_artifacts_sorted:
            for nc in session_artifacts.usercode_nodecollections:
                all_input_variables = sorted(list(nc.input_variables))
                artifact_user_input_variables = [
                    var
                    for var in all_input_variables
                    if var in unused_input_parameters
                ]
                user_input_var_typing_block = [
                    f"{var} = {session_input_parameters_spec[var].value_type}({var})"
                    for var in artifact_user_input_variables
                ]
                unused_input_parameters.difference_update(
                    set(artifact_user_input_variables)
                )
                input_var_loading_block = [
                    f"{var} = pickle.load(open('/tmp/{self.pipeline_name}/variable_{var}.pickle','rb'))"
                    for var in all_input_variables
                    if var not in artifact_user_input_variables
                ]
                function_call_block = BaseSessionWriter().get_session_artifact_function_call_block(
                    nc,
                    indentation=0,
                    source_module=f"{self.pipeline_name}_module",
                )
                return_var_saving_block = [
                    f"pickle.dump({var},open('/tmp/{self.pipeline_name}/variable_{var}.pickle','wb'))"
                    for var in nc.return_variables
                ]

                task_def: TaskDefinition = TaskDefinition(
                    function_name=nc.safename,
                    user_input_variables=artifact_user_input_variables,
                    typing_blocks=user_input_var_typing_block,
                    loading_blocks=input_var_loading_block,
                    call_block=function_call_block,
                    dumping_blocks=return_var_saving_block,
                )
                task_definitions[nc.safename] = task_def

        return task_definitions

    def get_session_task_definition(
        self,
    ) -> Dict[str, TaskDefinition]:
        """
        get_session_task_definition returns a task definition for each session in the pipeline.

        Returns a `task_definitions` dictionary, which maps a key corresponding to the task name to
        Linea's TaskDefinition object.
        Specific framework implementations of PipelineWriters should serialize the TaskDefinition
        objects to match the format for pipeline arguments that is expected by that framework.
        """
        task_definitions: Dict[str, TaskDefinition] = dict()

        for session_artifacts in self.session_artifacts_sorted:

            session_input_parameters_spec = (
                BaseSessionWriter().get_session_input_parameters_spec(
                    session_artifacts
                )
            )
            session_input_variables = list(
                session_input_parameters_spec.keys()
            )
            user_input_var_typing_block = [
                f"{var} = {session_input_parameters_spec[var].value_type}({var})"
                for var in session_input_variables
            ]

            input_var_loading_block: List[str] = []
            function_call_block = f"artifacts = {self.pipeline_name}_module.{BaseSessionWriter().get_session_function_call_block(session_artifacts)}"
            return_artifacts_saving_block = [
                f"pickle.dump(artifacts['{nc.name}'],open('/tmp/{self.pipeline_name}/artifact_{nc.safename}.pickle','wb'))"
                for nc in session_artifacts.usercode_nodecollections
                if isinstance(nc, ArtifactNodeCollection)
            ]
            function_name = BaseSessionWriter().get_session_function_name(
                session_artifacts
            )
            task_def: TaskDefinition = TaskDefinition(
                function_name=function_name,
                user_input_variables=session_input_variables,
                typing_blocks=user_input_var_typing_block,
                loading_blocks=input_var_loading_block,
                call_block=function_call_block,
                dumping_blocks=return_artifacts_saving_block,
            )

            task_definitions[function_name] = task_def

        return task_definitions
