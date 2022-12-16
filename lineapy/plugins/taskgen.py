"""
This taskgen files contains helper functions to create tasks.
"""
from typing import Dict

from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.graph_reader.node_collection import ArtifactNodeCollection
from lineapy.plugins.session_writers import BaseSessionWriter
from lineapy.plugins.task import DagTaskBreakdown, TaskDefinition
from lineapy.plugins.utils import load_plugin_template


def get_task_definitions(
    artifact_collection: ArtifactCollection,
    pipeline_name: str,
    task_breakdown: DagTaskBreakdown,
) -> Dict[str, TaskDefinition]:
    """
    get_task_definitions returns a dictionary of TaskDefinitions

    This function breaks down the artifact_collection into tasks based on the
    task_breakdown parameter. This will give the main bulk of tasks that should
    be included in a pipeline dag file.

    Returns a `task_definitions` dictionary, which maps a key corresponding to the task name to
    Linea's TaskDefinition object.
    Specific framework implementations of PipelineWriters should serialize the TaskDefinition
    objects to match the format for pipeline arguments that is expected by that framework.
    """
    if task_breakdown == DagTaskBreakdown.TaskAllSessions:
        return get_allsessions_task_definition(
            artifact_collection, pipeline_name
        )
    elif task_breakdown == DagTaskBreakdown.TaskPerSession:
        return get_session_task_definition(artifact_collection, pipeline_name)
    elif task_breakdown == DagTaskBreakdown.TaskPerArtifact:
        return get_artifact_task_definitions(
            artifact_collection, pipeline_name
        )
    else:
        raise ValueError(
            f"Task breakdown granularity {task_breakdown} is not currently supported."
        )


def get_artifact_task_definitions(
    artifact_collection: ArtifactCollection, pipeline_name: str
) -> Dict[str, TaskDefinition]:
    """
    get_artifact_task_definitions returns a task definition for each artifact the pipeline produces.
    This may include tasks that produce common variables that were not initially defined as artifacts.
    """
    task_definitions: Dict[str, TaskDefinition] = dict()
    unused_input_parameters = set(artifact_collection.input_parameters)

    for session_artifacts in artifact_collection.sort_session_artifacts():
        for nc in session_artifacts.usercode_nodecollections:
            all_input_variables = sorted(list(nc.input_variables))
            artifact_user_input_variables = [
                var
                for var in all_input_variables
                if var in unused_input_parameters
            ]
            session_input_parameters_spec = (
                BaseSessionWriter().get_session_input_parameters_spec(
                    session_artifacts
                )
            )
            user_input_var_typing_block = [
                f"{var} = {session_input_parameters_spec[var].value_type}({var})"
                for var in artifact_user_input_variables
            ]
            unused_input_parameters.difference_update(
                set(artifact_user_input_variables)
            )
            loaded_input_vars = [
                var
                for var in all_input_variables
                if var not in artifact_user_input_variables
            ]
            function_call_block = (
                BaseSessionWriter().get_session_artifact_function_call_block(
                    nc,
                    source_module=f"{pipeline_name}_module",
                )
            )

            task_def: TaskDefinition = TaskDefinition(
                function_name=nc.safename,
                user_input_variables=artifact_user_input_variables,
                loaded_input_variables=loaded_input_vars,
                typing_blocks=user_input_var_typing_block,
                call_block=function_call_block,
                return_vars=nc.return_variables,
                pipeline_name=pipeline_name,
            )
            task_definitions[nc.safename] = task_def

    return task_definitions


def get_session_task_definition(
    artifact_collection: ArtifactCollection, pipeline_name: str
) -> Dict[str, TaskDefinition]:
    """
    get_session_task_definition returns a task definition for each session in the pipeline.
    """
    task_definitions: Dict[str, TaskDefinition] = dict()

    for session_artifacts in artifact_collection.sort_session_artifacts():

        session_input_parameters_spec = (
            BaseSessionWriter().get_session_input_parameters_spec(
                session_artifacts
            )
        )
        session_input_variables = list(session_input_parameters_spec.keys())
        user_input_var_typing_block = [
            f"{var} = {session_input_parameters_spec[var].value_type}({var})"
            for var in session_input_variables
        ]

        return_vars = [
            nc.safename
            for nc in session_artifacts.usercode_nodecollections
            if isinstance(nc, ArtifactNodeCollection)
        ]

        raw_function_call_block = (
            BaseSessionWriter().get_session_function_callblock(
                session_artifacts
            )
        )
        # Call module's run session function and unpack the artifacts from it
        function_call_block = (
            f"artifacts = {pipeline_name}_module.{raw_function_call_block}\n"
            + "\n".join(
                f'{nc.safename} = artifacts["{nc.name}"]'
                for nc in session_artifacts.usercode_nodecollections
                if isinstance(nc, ArtifactNodeCollection)
            )
        )

        function_name = BaseSessionWriter().get_session_function_name(
            session_artifacts
        )

        task_def: TaskDefinition = TaskDefinition(
            function_name=function_name,
            user_input_variables=session_input_variables,
            loaded_input_variables=[],
            typing_blocks=user_input_var_typing_block,
            call_block=function_call_block,
            return_vars=return_vars,
            pipeline_name=pipeline_name,
        )

        task_definitions[function_name] = task_def

    return task_definitions


def get_allsessions_task_definition(
    artifact_collection: ArtifactCollection,
    pipeline_name: str,
) -> Dict[str, TaskDefinition]:
    """
    get_allsessions_task_definition returns a single task definition for the whole pipeline.
    """

    indentation_block = " " * 4
    return {
        "run_all": TaskDefinition(
            function_name="run_all",
            user_input_variables=artifact_collection.input_parameters,
            loaded_input_variables=[],
            typing_blocks=[],
            call_block=f"{indentation_block}artifacts = {pipeline_name}_module.run_all_sessions()"
            "",
            return_vars=["artifacts"],
            pipeline_name=pipeline_name,
        )
    }


def get_localpickle_setup_task_definition(pipeline_name):
    """
    Returns a TaskDefinition that is used to set up pipeline that uses local pickle type
    serialization for inter task communication.

    This task should be used at the beginning of a pipeline.
    """
    TASK_LOCALPICKLE_SETUP_TEMPLATE = load_plugin_template(
        "task/localpickle/task_local_pickle_setup.jinja"
    )
    call_block = TASK_LOCALPICKLE_SETUP_TEMPLATE.render(
        pipeline_name=pipeline_name
    )
    return TaskDefinition(
        function_name="dag_setup",
        user_input_variables=[],
        loaded_input_variables=[],
        typing_blocks=[],
        call_block=call_block,
        return_vars=[],
        pipeline_name=pipeline_name,
    )


def get_localpickle_teardown_task_definition(pipeline_name):
    """
    Returns a TaskDefinition that is used to teardown a pipeline that uses local pickle type
    serialization for inter task communication.

    This task should be used at the end of a pipeline.

    """
    TASK_LOCALPICKLE_TEARDOWN_TEMPLATE = load_plugin_template(
        "task/localpickle/task_local_pickle_teardown.jinja"
    )
    call_block = TASK_LOCALPICKLE_TEARDOWN_TEMPLATE.render(
        pipeline_name=pipeline_name
    )
    return TaskDefinition(
        function_name="dag_teardown",
        user_input_variables=[],
        loaded_input_variables=[],
        typing_blocks=[],
        call_block=call_block,
        return_vars=[],
        pipeline_name=pipeline_name,
    )
