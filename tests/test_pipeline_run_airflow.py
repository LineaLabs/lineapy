import subprocess
from pathlib import Path

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writer_factory import PipelineWriterFactory


@pytest.mark.airflow
@pytest.mark.slow
@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies, dag_config, input_parameters",
    [
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "airflow_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            {},
            [],
            id="airflow_pipeline_housing_w_dependencies",
        ),
    ],
)
def test_run_airflow_dag(
    virtualenv,
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    pipeline_name,
    dependencies,
    dag_config,
    input_parameters,
):
    """
    Verifies that the "--airflow" CLI command produces a working Airflow DAG
    by running the DAG locally.

    Depends on snapshot being available from previous test.
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

    # Write out pipeline files
    artifact_def_list = [get_lineaartifactdef(art) for art in artifact_list]
    artifact_collection = ArtifactCollection(
        linea_db, artifact_def_list, input_parameters=input_parameters
    )

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType["AIRFLOW"],
        artifact_collection=artifact_collection,
        dependencies=dependencies,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        dag_config=dag_config,
    )
    pipeline_writer.write_pipeline_files()

    airflow_home = tmp_path / "airflow"
    airflow_home.mkdir()
    dags_home = airflow_home / "dags"
    dags_home.mkdir()

    # Copy the dag and the data
    # NOTE: We can't leave them in the tests folder, since there are other
    # files in there that airflow will attempt to import, and fail, since
    # those dependencies are not in the virtualenv.

    ex = None
    try:
        ex = subprocess.check_call(
            [
                "cp",
                "-f",
                f"{tmp_path}/{pipeline_name}_module.py",
                f"{tmp_path}/{pipeline_name}_dag.py",
                str(dags_home),
            ]
        )
    except Exception as e:
        print(ex)
        print(e)
        raise ValueError

    # Run airflow in new virtual env so we don't end up with version conflicts
    # with lineapy deps
    # https://github.com/man-group/pytest-plugins/tree/master/pytest-virtualenv#installing-packages
    virtualenv.run(
        "pip install -r airflow-requirements.txt", capture=False, cd="."
    )

    # Set the airflow home for subsequent calls
    virtualenv.env["AIRFLOW_HOME"] = str(airflow_home)
    # We create a new DB for airflow for testing, so it's reproducible
    virtualenv.run("airflow db init", capture=False)
    virtualenv.run(
        f"airflow dags test {pipeline_name}_dag 2020-10-19",
        capture=False,
        # Run in current root lineapy so that relative paths are accurate
        # cd=".",
    )
