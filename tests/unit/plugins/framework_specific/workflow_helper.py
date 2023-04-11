from pathlib import Path

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import WorkflowType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.workflow_writer_factory import WorkflowWriterFactory


def workflow_file_generation_helper(
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    framework,
    workflow_name,
    dependencies,
    dag_config,
    input_parameters,
):
    """
    Helper function for tests that need to run workflow writers.

    Runs input_script1, then input_script2, and then creates workflow files
    in tmp_path based on the other parameters to config the workflow.
    """

    code1 = Path(
        "tests", "unit", "graph_reader", "inputs", input_script1
    ).read_text()
    execute(code1, snapshot=False)

    if input_script2 != "":
        code2 = Path(
            "tests", "unit", "graph_reader", "inputs", input_script2
        ).read_text()
        execute(code2, snapshot=False)

    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(
        linea_db,
        artifact_def_list,
        input_parameters=input_parameters,
        dependencies=dependencies,
    )

    # Construct workflow writer
    workflow_writer = WorkflowWriterFactory.get(
        workflow_type=WorkflowType[framework],
        artifact_collection=artifact_collection,
        workflow_name=workflow_name,
        output_dir=tmp_path,
        dag_config=dag_config,
    )

    # Write out workflow files
    workflow_writer.write_workflow_files()
