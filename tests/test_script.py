import io
import json
import os
import pathlib
import subprocess
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from click import BadParameter

from lineapy.cli.cli import (
    annotations_add,
    annotations_delete,
    annotations_list,
    python_cli,
    remove_annotations_file_extension,
    validate_annotations_path,
)
from lineapy.plugins.utils import slugify
from lineapy.utils.config import options
from tests.util import clean_lineapy_env_var


@pytest.mark.slow
def test_cli_entrypoint():
    """
    Verifies that the "--help" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


@pytest.mark.slow
def test_lineapy_init_with_options():
    """
    Verify that `lineapy init` generate with different type of cli options input
    """
    temp_dir_name = tempfile.mkdtemp()
    subprocess.check_call(
        [
            "lineapy",
            "--home-dir",
            temp_dir_name,
            "--do-not-track=true",
            "--logging-level=debug",
            "--mlflow-tracking-uri=sqlite://",
            "--default-ml-models-storage-backend=mlflow",
            "init",
        ]
    )

    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)

    assert Path(temp_dir_name).joinpath("lineapy_config.json").exists()
    assert generated_config["home_dir"] == temp_dir_name
    assert generated_config["do_not_track"] == "True"
    assert generated_config["logging_level"] == "DEBUG"
    assert generated_config["mlflow_tracking_uri"] == "sqlite://"
    assert generated_config["default_ml_models_storage_backend"] == "mlflow"


@pytest.mark.slow
def test_config_order():

    temp_dir_name = tempfile.mkdtemp()

    # No config file, use default value logging_level=="INFO"
    existing_lineapy_env = clean_lineapy_env_var()
    subprocess.check_call(["lineapy", "--home-dir", temp_dir_name, "init"])
    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)
    assert generated_config["logging_level"] == "INFO"

    # With config file as 'INFO', use CLI option logging_level=='DEBUG'
    clean_lineapy_env_var()
    subprocess.check_call(
        [
            "lineapy",
            "--home-dir",
            temp_dir_name,
            "--logging-level=DEBUG",
            "init",
        ]
    )
    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)
    assert generated_config["logging_level"] == "DEBUG"

    # With config file as 'DEBUG', use config file logging_level=='DEBUG'
    clean_lineapy_env_var()
    os.environ["LINEAPY_HOME_DIR"] = temp_dir_name
    subprocess.check_call(["lineapy", "init"])
    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)
    assert generated_config["logging_level"] == "DEBUG"

    # With config file as 'DEBUG' and env var as 'INFO', use env var logging_level='INFO'
    clean_lineapy_env_var()
    os.environ["LINEAPY_HOME_DIR"] = temp_dir_name
    os.environ["LINEAPY_LOGGING_LEVEL"] = "INFO"
    subprocess.check_call(["lineapy", "init"])
    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)
    assert generated_config["logging_level"] == "INFO"

    # With config file as 'INFO' and env var as 'DEBUG', use CLI option logging_level='NOTSET'
    clean_lineapy_env_var()
    os.environ["LINEAPY_HOME_DIR"] = temp_dir_name
    os.environ["LINEAPY_LOGGING_LEVEL"] = "DEBUG"
    subprocess.check_call(["lineapy", "--logging-level=NOTSET", "init"])
    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)
    assert generated_config["logging_level"] == "NOTSET"

    # Reset to original env variables
    clean_lineapy_env_var()
    for k, v in existing_lineapy_env.items():
        os.environ[k] = v


@pytest.mark.slow
def test_pass_arg():
    """
    Verifies that the arg is pass into the command
    """
    code = """import sys
import lineapy
lineapy.save(sys.argv[1], "first_arg")"""
    with tempfile.NamedTemporaryFile() as f:
        f.write(code.encode())
        f.flush()
        python_cli(
            file_name=pathlib.Path(f.name), slice=["first_arg"], arg=["an arg"]
        )


@pytest.mark.slow
def test_slice_housing():
    """
    Verifies that the "--slice" CLI command is aliased to the `lineapy` executable
    """
    python_cli(file_name=pathlib.Path("tests/housing.py"), slice=["p value"])


@pytest.mark.slow
def test_slice_housing_multiple():
    """
    Verifies that we can run "--slice" CLI command multiple times
    """
    python_cli(
        file_name=pathlib.Path("tests/housing.py"), slice=["p value", "y"]
    )


def test_slice_housing_airflow():
    """
    Verifies that the "--airflow" CLI command is aliased to the `lineapy` executable
    """
    with tempfile.TemporaryDirectory() as output_dir:
        python_cli(
            file_name=pathlib.Path("tests/housing.py"),
            slice=["p value", "y"],
            export_slice_to_airflow_dag="sliced_housing_dag",
            export_dir=output_dir,
            airflow_task_dependencies="{'p value': {'y'}}",
        )


@pytest.mark.slow
def test_export_slice_housing():
    """
    Verifies that the "--export-slice" CLI command is aliased to the `lineapy` executable
    """
    python_cli(
        file_name=pathlib.Path("tests/housing.py"),
        slice=["p value"],
        export_slice=["sliced_housing"],
    )


@pytest.mark.slow
def test_export_slice_housing_multiple():
    """
    Verifies that we can run "--export-slice" CLI command multiple times
    """
    python_cli(
        file_name=pathlib.Path("tests/housing.py"),
        slice=["p value", "y"],
        export_slice=["p_value_housing", "y_housing"],
    )


def assert_annotations_count(n=0):
    f = io.StringIO()
    with redirect_stdout(f):
        annotations_list()
    out = f.getvalue()
    if n > 0:
        assert len(str(out.strip()).split("\n")) == n
    else:
        assert len(out) == n


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_annotate_list(move_folder):
    """Verifies existence of 'lineapy annotate list'"""
    assert_annotations_count()


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_annotate_add_invalid_path(tmp_path, move_folder):
    """
    Verifies failure of adding non-existent path.
    """
    invalid_path = tmp_path / "nonexistent.yaml"
    with pytest.raises(FileNotFoundError):
        annotations_add(pathlib.Path(str(invalid_path)))

    assert_annotations_count()


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_annotate_add_non_yaml_file(move_folder):
    """
    Verifies failure of adding file that does not end in '.yaml'.
    """
    valid_yaml = """

- module: keras.engine.training
  annotations:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """
    with tempfile.NamedTemporaryFile(suffix=".not-yaml") as f:
        f.write(valid_yaml.encode())
        f.flush()
        with pytest.raises(BadParameter):
            # this is called as a callback in click argument
            validate_annotations_path(None, None, pathlib.Path(f.name))
            annotations_add(pathlib.Path(f.name))

    assert_annotations_count()


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_annotate_add_invalid_yaml(move_folder):
    """
    Verifies failure of adding invalid spec.
    """
    invalid_yaml = """

- module: keras.engine.training
  error in yaml
  annotations:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(invalid_yaml.encode())
        f.flush()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            validate_annotations_path(None, None, pathlib.Path(f.name))
            annotations_add(pathlib.Path(f.name))

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

    assert_annotations_count()


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_annotate_add_valid_yaml(move_folder):
    """
    Verifies success of adding valid spec.
    """
    valid_yaml = """

- module: keras.engine.training
  annotations:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(valid_yaml.encode())
        f.flush()
        annotations_add(pathlib.Path(f.name))

    assert_annotations_count(1)


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_annotate_delete_invalid_path(tmp_path, move_folder):
    """
    Verifies failure of deleting non-existent source.
    """
    invalid_path = tmp_path / "nonexistent.yaml"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        annotations_delete(str(invalid_path))

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


@pytest.mark.folder(options.safe_get("customized_annotation_folder"))
def test_delete_existing_source(move_folder):
    """
    Verifies success of deleting source.
    """
    valid_yaml = """

- module: keras.engine.training
  annotations:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(valid_yaml.encode())
        f.flush()
        annotations_add(pathlib.Path(f.name))

    source_name = os.path.basename(f.name)
    source_name = remove_annotations_file_extension(source_name)
    source_name = slugify(source_name)
    annotations_delete(os.path.basename(source_name))
    assert_annotations_count()


@pytest.mark.parametrize(
    "code",
    (
        "+++",
        "1 / 0",
        "1\nx",
        "import lineapy.utils.__error_on_load",
        "import lineapy_xxx",
    ),
    ids=(
        "syntax error",
        "runtime error",
        "name error",
        "error in import",
        "invalid import",
    ),
)
def test_linea_python_equivalent(tmp_path, code):
    """
    Verifies that Python and lineapy have the same stack trace.
    """
    f = tmp_path / "script.py"
    f.write_text(code)

    linea_run = subprocess.run(
        ["lineapy", "python", str(f)],
        capture_output=True,
    )
    python_run = subprocess.run(["python", str(f)], capture_output=True)
    assert linea_run.returncode == python_run.returncode
    assert linea_run.stdout.decode() == python_run.stdout.decode()
    assert linea_run.stderr.decode() == python_run.stderr.decode()


def test_ipython():
    raw_code = 'import lineapy; print(lineapy.save(1, "one").get_code())'
    clean_code = (
        """import lineapy\n\nprint(lineapy.save(1, "one").get_code())"""
    )
    res = subprocess.check_output(["lineapy", "ipython", "-c", raw_code])
    assert res.decode().strip().endswith(clean_code)
