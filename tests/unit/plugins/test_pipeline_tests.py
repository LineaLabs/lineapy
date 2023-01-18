import pickle
from pathlib import Path

import pytest

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writer_factory import PipelineWriterFactory
from lineapy.plugins.utils import slugify


def check_requirements_txt(t1: str, t2: str):
    return set(t1.split("\n")) == set(t2.split("\n"))


@pytest.mark.parametrize(
    "input_script1, input_script2, artifact_list, pipeline_name, dependencies",
    [
        pytest.param(
            "simple",
            "complex",
            ["a0", "b0"],
            "script_pipeline_a0_b0_dependencies",
            {"a0": {"b0"}},
            id="script_pipeline_a0_b0_dependencies",
        ),
        pytest.param(
            "complex",
            "",
            ["f", "h"],
            "script_complex_h",
            {},
            id="script_complex_h",
        ),
        pytest.param(
            "housing",
            "",
            ["y", "p value"],
            "script_pipeline_housing_w_dependencies",
            {"p value": {"y"}},
            id="script_pipeline_housing_w_dependencies",
        ),
    ],
)
def test_pipeline_test_generation(
    tmp_path,
    linea_db,
    execute,
    input_script1,
    input_script2,
    artifact_list,
    pipeline_name,
    dependencies,
    snapshot,
):
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
        dependencies=dependencies,
    )

    # Construct pipeline writer
    pipeline_writer = PipelineWriterFactory.get(
        pipeline_type=PipelineType.SCRIPT,
        artifact_collection=artifact_collection,
        pipeline_name=pipeline_name,
        output_dir=tmp_path,
        generate_test=True,
    )

    # Write out pipeline files
    pipeline_writer.write_pipeline_files()

    # Compare generated vs. expected
    path_generated = Path(tmp_path, f"test_{pipeline_name}.py")
    content_generated = path_generated.read_text()
    assert content_generated == snapshot

    # Check if artifact values have been (re-)stored
    # to serve as "ground truths" for pipeline testing
    for artname in artifact_list:
        path_generated = Path(
            tmp_path, "sample_output", f"{slugify(artname)}.pkl"
        )
        path_expected = Path(
            "tests",
            "unit",
            "plugins",
            "expected",
            pipeline_name,
            "sample_output",
            f"{slugify(artname)}.pkl",
        )
        with path_generated.open("rb") as fp:
            content_generated = pickle.load(fp)
        with path_expected.open("rb") as fp:
            content_expected = pickle.load(fp)
        assert type(content_generated) == type(content_expected)
