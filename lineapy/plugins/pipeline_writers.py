import itertools
import logging
import pickle
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Union

import networkx as nx

from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import (
    ArtifactCollection,
    SessionArtifacts,
)
from lineapy.graph_reader.node_collection import (
    ArtifactNodeCollection,
    UserCodeNodeCollection,
)
from lineapy.graph_reader.types import InputVariable
from lineapy.plugins.session_writers import BaseSessionWriter
from lineapy.plugins.task import (
    AirflowDagConfig,
    AirflowDagFlavor,
    DVCDagConfig,
    DVCDagFlavor,
    TaskDefinition,
    TaskGraph,
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
                BaseSessionWriter().get_session_module_imports(
                    sa, self.include_non_slice_as_comment
                )
                for sa in self.session_artifacts_sorted
            ]
        )

        artifact_function_definition = "\n".join(
            list(
                itertools.chain.from_iterable(
                    [
                        BaseSessionWriter().get_session_artifact_function_definitions(
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
                    include_non_slice_as_comment=self.include_non_slice_as_comment,
                    indentation=indentation,
                )
                for sa in self.session_artifacts_sorted
            ]
        )

        module_function_body = "\n".join(
            [
                f"{indentation_block}{return_dict_name}.update({BaseSessionWriter().get_session_function_callblock(sa)})"
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


class AirflowPipelineWriter(BasePipelineWriter):
    """
    Class for pipeline file writer. Corresponds to "AIRFLOW" framework.
    """

    @property
    def docker_template_name(self) -> str:
        return "airflow_dockerfile.jinja"

    def _write_dag(self) -> None:
        dag_flavor = self.dag_config.get(
            "dag_flavor", "PythonOperatorPerArtifact"
        )

        # Check if the given DAG flavor is a supported/valid one
        if dag_flavor not in AirflowDagFlavor.__members__:
            raise ValueError(
                f'"{dag_flavor}" is an invalid airflow dag flavor.'
            )

        # Construct DAG text for the given flavor
        if (
            AirflowDagFlavor[dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerSession
        ):
            full_code = self._write_operator_per_session()
        elif (
            AirflowDagFlavor[dag_flavor]
            == AirflowDagFlavor.PythonOperatorPerArtifact
        ):
            full_code = self._write_operator_per_artifact()

        # Write out file
        file = self.output_dir / f"{self.pipeline_name}_dag.py"
        file.write_text(prettify(full_code))
        logger.info(f"Generated DAG file: {file}")

    def _write_operator_per_session(self) -> str:
        """
        This hidden method implements Airflow DAG code generation corresponding
        to the `PythonOperatorPerSession` flavor, where each session gets its
        own Python operator. For instance, if the two artifacts in our pipeline
        (e.g., model and prediction) were created in the same session, we would
        get an Airflow DAG file looking as the following:

        .. code-block:: python
        def dag_setup():
            pickle_folder = pathlib.Path("/tmp").joinpath("g2_z")
            if not pickle_folder.exists():
                pickle_folder.mkdir()


        def dag_teardown():
            pickle_files = pathlib.Path("/tmp").joinpath("g2_z").glob("*.pickle")
            for f in pickle_files:
                f.unlink()

            def task_run_session_including_g2():
                artifacts = g2_z_module.run_session_including_g2()
                pickle.dump(artifacts["g2"], open("/tmp/g2_z/artifact_g2.pickle", "wb"))
                pickle.dump(artifacts["z"], open("/tmp/g2_z/artifact_z.pickle", "wb"))

            with DAG(...) as dag:
                setup = PythonOperator(
                    task_id="dag_setup",
                    python_callable=dag_setup,
                )

                teardown = PythonOperator(
                    task_id="dag_teardown",
                    python_callable=dag_teardown,
                )

                run_session_including_g2 = PythonOperator(
                    task_id="run_session_including_g2_task",
                    python_callable=task_run_session_including_g2,
                )

                setup >> run_session_including_g2
                run_session_including_g2 >> teardown

            run_session_including_g2

        This way, the generated Airflow DAG file opens room for engineers
        to peak and control pipeline runs at a finer level and allows
        for further customization.
        """
        codegenerator = AirflowCodeGenerator(self.artifact_collection)
        DAG_TEMPLATE = load_plugin_template("airflow_dag_PythonOperator.jinja")
        task_functions = []
        task_definitions = []
        for sa in self.session_artifacts_sorted:
            task_functions.append(
                BaseSessionWriter().get_session_function_name(sa)
            )
            task_definitions.append(
                get_session_task_definition(sa, self.pipeline_name)
            )
        dependencies = {
            task_functions[i + 1]: {task_functions[i]}
            for i in range(len(task_functions) - 1)
        }
        task_graph = TaskGraph(
            nodes=task_functions,
            mapping={f: f for f in task_functions},
            edges=dependencies,
        )
        session_function_params = (
            codegenerator.get_session_function_params_args()
        )
        tasks = [
            {"name": ft, "op_kwargs": session_function_params.get(ft, None)}
            for ft in task_functions
        ]
        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.pipeline_name,
            MODULE_NAME=self.pipeline_name + "_module",
            OWNER=self.dag_config.get("owner", "airflow"),
            RETRIES=self.dag_config.get("retries", 2),
            START_DATE=self.dag_config.get("start_date", "days_ago(1)"),
            SCHEDULE_INTERVAL=self.dag_config.get(
                "schedule_interval", "*/15 * * * *"
            ),
            MAX_ACTIVE_RUNS=self.dag_config.get("max_active_runs", 1),
            CATCHUP=self.dag_config.get("catchup", "False"),
            dag_params=codegenerator.get_params_args(),
            task_definitions=task_definitions,
            tasks=tasks,
            task_dependencies=task_graph.get_airflow_dependencies(
                setup_task="setup", teardown_task="teardown"
            ),
        )

        return full_code

    def _write_operator_per_artifact(self) -> str:
        """
        This method implements Airflow DAG code generation corresponding to the
        `PythonOperatorPerArtifact` flavor, where each artifact gets its own
        Python operator. For instance, if the two artifacts in our pipeline
        (e.g., model and prediction) were created in the same session, we would
        get an Airflow DAG file looking as the following:

        .. code-block:: python
            import pickle
            import iris_module

            ...

            def task_iris_model():
                mod = iris_module.get_iris_model()
                pickle.dump(mod, open("/tmp/iris/variable_mod.pickle", "wb"))

            def task_iris_pred():
                mod = pickle.load(open("/tmp/iris/variable_mod.pickle", "rb"))
                pred = iris_module.get_iris_pred(mod)
                pickle.dump(
                    pred, open("/tmp/iris/variable_pred.pickle", "wb")
                )

            with DAG(...) as dag:
                iris_model = PythonOperator(
                    task_id="iris_model_task",
                    python_callable=task_iris_model,
                )

                iris_pred = PythonOperator(
                    task_id="iris_pred_task",
                    python_callable=task_iris_pred,
                )

            iris_model >> iris_pred

        This way, the generated Airflow DAG file opens room for engineers
        to peak and control pipeline runs at a finer level and allows
        for further customization.
        """
        codegenerator = AirflowCodeGenerator(self.artifact_collection)
        DAG_TEMPLATE = load_plugin_template("airflow_dag_PythonOperator.jinja")
        task_def = self.get_artifact_task_definitions()
        task_functions = list(task_def.keys())
        task_definitions = [task["definition"] for task in task_def.values()]
        dependencies = {
            task_functions[i + 1]: {task_functions[i]}
            for i in range(len(task_functions) - 1)
        }
        task_graph = TaskGraph(
            nodes=task_functions,
            mapping={f: f for f in task_functions},
            edges=dependencies,
        )
        artifact_function_params = (
            codegenerator.get_artifact_function_params_args(task_def)
        )
        tasks = [
            {"name": ft, "op_kwargs": artifact_function_params.get(ft, None)}
            for ft in task_functions
        ]
        full_code = DAG_TEMPLATE.render(
            DAG_NAME=self.pipeline_name,
            MODULE_NAME=self.pipeline_name + "_module",
            OWNER=self.dag_config.get("owner", "airflow"),
            RETRIES=self.dag_config.get("retries", 2),
            START_DATE=self.dag_config.get("start_date", "days_ago(1)"),
            SCHEDULE_INTERVAL=self.dag_config.get(
                "schedule_interval", "*/15 * * * *"
            ),
            dag_params=codegenerator.get_params_args(),
            MAX_ACTIVE_RUNS=self.dag_config.get("max_active_runs", 1),
            CATCHUP=self.dag_config.get("catchup", "False"),
            task_definitions=task_definitions,
            tasks=tasks,
            task_dependencies=task_graph.get_airflow_dependencies(
                setup_task="setup", teardown_task="teardown"
            ),
        )

        return full_code

    def get_artifact_task_definitions(
        self, indentation=4
    ) -> Dict[str, TaskDefinition]:
        """
        Add deserialization of input variables and serialization of output
        variables logic of the artifact fucntion call_block and wrap them into a
        new function definition.
        """
        task_definitions: Dict[str, TaskDefinition] = dict()
        unused_input_parameters = set(
            self.artifact_collection.input_parameters
        )
        for session_artifacts in self.session_artifacts_sorted:
            session_input_parameters_spec = (
                BaseSessionWriter().get_session_input_parameters_spec(
                    session_artifacts
                )
            )
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
                function_call_block = (
                    BaseSessionWriter().get_function_call_block(
                        nc,
                        indentation=0,
                        source_module=f"{self.pipeline_name}_module",
                    )
                )
                return_var_saving_block = [
                    f"pickle.dump({var},open('/tmp/{self.pipeline_name}/variable_{var}.pickle','wb'))"
                    for var in nc.return_variables
                ]
                TASK_FUNCTION_TEMPLATE = load_plugin_template(
                    "task_function.jinja"
                )
                function_definition = TASK_FUNCTION_TEMPLATE.render(
                    function_name=nc.safename,
                    user_input_variables=", ".join(
                        artifact_user_input_variables
                    ),
                    typing_blocks=user_input_var_typing_block,
                    loading_blocks=input_var_loading_block,
                    call_block=function_call_block,
                    dumping_blocks=return_var_saving_block,
                    indentation_block=" " * indentation,
                )
                task_def: TaskDefinition = {
                    "definition": function_definition,
                    "user_input_variables": artifact_user_input_variables,
                }
                task_definitions[nc.safename] = task_def

        return task_definitions


def get_session_task_definition(
    sa: SessionArtifacts,
    pipeline_name: str,
    indentation=4,
) -> str:
    """
    Add serialization of output artifacts logic of the session function
    call_block and wrap them into a new function definition.
    """
    session_input_parameters_spec = (
        BaseSessionWriter().get_session_input_parameters_spec(sa)
    )
    session_input_variables = list(session_input_parameters_spec.keys())
    user_input_var_typing_block = [
        f"{var} = {session_input_parameters_spec[var].value_type}({var})"
        for var in session_input_variables
    ]

    input_var_loading_block: List[str] = []
    function_call_block = f"artifacts = {pipeline_name}_module.{BaseSessionWriter().get_session_function_callblock(sa)}"
    return_artifacts_saving_block = [
        f"pickle.dump(artifacts['{nc.name}'],open('/tmp/{pipeline_name}/artifact_{nc.safename}.pickle','wb'))"
        for nc in sa.usercode_nodecollections
        if isinstance(nc, ArtifactNodeCollection)
    ]

    TASK_FUNCTION_TEMPLATE = load_plugin_template("task_function.jinja")
    return TASK_FUNCTION_TEMPLATE.render(
        function_name=BaseSessionWriter().get_session_function_name(sa),
        user_input_variables=", ".join(session_input_variables),
        typing_blocks=user_input_var_typing_block,
        loading_blocks=input_var_loading_block,
        call_block=function_call_block,
        dumping_blocks=return_artifacts_saving_block,
        indentation_block=" " * indentation,
    )


class AirflowCodeGenerator:
    def __init__(self, ac: ArtifactCollection) -> None:
        self.artifact_collection = ac

    def get_params_args(self) -> str:
        input_parameters_dict = dict()
        for sa in self.artifact_collection.sort_session_artifacts():
            for input_spec in (
                BaseSessionWriter()
                .get_session_input_parameters_spec(sa)
                .values()
            ):
                input_parameters_dict[
                    input_spec.variable_name
                ] = input_spec.value
        return '"params":' + str(input_parameters_dict)

    def get_session_function_params_args(self) -> Dict[str, str]:
        session_function_input_parameters = dict()
        for sa in self.artifact_collection.sort_session_artifacts():
            session_input_parameters = list(sa.input_parameters_node.keys())
            if len(session_input_parameters) > 0:
                session_function_input_parameters[
                    BaseSessionWriter().get_session_function_name(sa)
                ] = "op_kwargs=" + str(
                    {
                        var: "{{ params." + var + " }}"
                        for var in session_input_parameters
                    }
                )
        return session_function_input_parameters

    def get_artifact_function_params_args(
        self, artifact_function_definitions: Dict[str, TaskDefinition]
    ) -> Dict[str, str]:
        artifact_function_input_parameters = dict()
        for sa in self.artifact_collection.sort_session_artifacts():
            session_input_parameters = set(sa.input_parameters_node.keys())
            for nc in sa.usercode_nodecollections:
                user_input_variables = artifact_function_definitions[
                    nc.safename
                ]["user_input_variables"]
                parameterized_variables = nc.input_variables.intersection(
                    session_input_parameters
                ).intersection(set(user_input_variables))
                if len(parameterized_variables) > 0:
                    artifact_function_input_parameters[
                        nc.safename
                    ] = "op_kwargs=" + str(
                        {
                            var: "{{ params." + var + " }}"
                            for var in sorted(list(parameterized_variables))
                        }
                    )
        return artifact_function_input_parameters


class DVCPipelineWriter(BasePipelineWriter):
    def _write_dag(self) -> None:
        dag_flavor = self.dag_config.get(
            "dag_flavor", "SingleStageAllSessions"
        )

        # Check if the given DAG flavor is a supported/valid one
        if dag_flavor not in DVCDagFlavor.__members__:
            raise ValueError(f'"{dag_flavor}" is an invalid dvc dag flavor.')

        # Construct DAG text for the given flavor
        if DVCDagFlavor[dag_flavor] == DVCDagFlavor.SingleStageAllSessions:
            full_code = self._write_operator_run_all_sessions()

        # Write out file
        file = self.output_dir / "dvc.yaml"
        file.write_text(full_code)
        logger.info(f"Generated DAG file: {file}")

    def _write_operator_run_all_sessions(self) -> str:
        """
        This hidden method implements DVC DAG code generation corresponding
        to the `SingleStageAllSessions` flavor. This DAG only has one stage and
        calls `run_all_sessions` generated by the module file.
        """

        DAG_TEMPLATE = load_plugin_template(
            "dvc_dag_SingleStageAllSessions.jinja"
        )

        full_code = DAG_TEMPLATE.render(
            MODULE_COMMAND=f"python {self.pipeline_name}_module.py",
        )

        return full_code

    @property
    def docker_template_name(self) -> str:
        return "dvc_dockerfile.jinja"


class PipelineWriterFactory:
    @classmethod
    def get(
        cls,
        pipeline_type: PipelineType = PipelineType.SCRIPT,
        *args,
        **kwargs,
    ):
        if pipeline_type == PipelineType.AIRFLOW:
            return AirflowPipelineWriter(*args, **kwargs)
        elif pipeline_type == PipelineType.DVC:
            return DVCPipelineWriter(*args, **kwargs)
        else:
            return BasePipelineWriter(*args, **kwargs)
