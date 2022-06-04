import json
import os
import pathlib
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from lineapy.cli.cli import python_cli, remove_annotations_file_extension
from lineapy.plugins.utils import slugify
from lineapy.utils.config import options


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
            "--do-not-track",
            "--logging-level=debug",
            "init",
        ]
    )

    with open(Path(temp_dir_name).joinpath("lineapy_config.json"), "r") as f:
        generated_config = json.load(f)

    assert Path(temp_dir_name).joinpath("lineapy_config.json").exists()
    assert generated_config["home_dir"] == temp_dir_name
    assert generated_config["do_not_track"] == "True"
    assert generated_config["logging_level"] == "DEBUG"


@pytest.mark.slow
def test_config_order():
    def clean_lineapy_env_var():
        existing_lineapy_env = {
            x: os.environ[x]
            for x in os.environ.keys()
            if x.startswith("LINEAPY_")
        }
        for key in existing_lineapy_env.keys():
            del os.environ[key]
        return existing_lineapy_env

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


@pytest.fixture
def annotations_folder():
    """
    Fixture for annotate commands. It moves user's
    '.lineapy/custom-annotations'dir and
    replaces it with a temp for testing.
    """
    current_path = Path(options.safe_get("customized_annotation_folder"))
    current_path_str = str(current_path.resolve())
    old_path = current_path.parent.joinpath(current_path.name + ".old")
    old_path_str = str(old_path.resolve())

    # If 'custom-annotations.old exists already, the test was canceled
    # early previously. Clean up 'custom-annotations' folder from
    # previous run.
    if old_path.exists():
        shutil.rmtree(current_path_str, ignore_errors=True)
    else:
        shutil.move(current_path_str, old_path_str)

    yield

    # clean up test-generated directories
    if current_path.exists():
        shutil.rmtree(current_path_str)
    if old_path.exists():
        shutil.move(old_path_str, current_path_str)


@pytest.mark.slow
def test_annotate_list(annotations_folder):
    """Verifies existence of 'lineapy annotate list'"""
    proc = subprocess.run(
        ["lineapy", "annotate", "list"], check=True, capture_output=True
    )
    assert len(proc.stdout) == 0


@pytest.mark.slow
def test_annotate_add_invalid_path(tmp_path, annotations_folder):
    """
    Verifies failure of adding non-existent path.
    """
    invalid_path = tmp_path / "nonexistent.yaml"
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(
            ["lineapy", "annotate", "add", str(invalid_path)]
        )

    proc = subprocess.run(
        ["lineapy", "annotate", "list"], check=True, capture_output=True
    )
    assert len(proc.stdout) == 0


@pytest.mark.slow
def test_annotate_add_non_yaml_file(annotations_folder):
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
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_call(["lineapy", "annotate", "add", f.name])

    proc = subprocess.run(
        ["lineapy", "annotate", "list"], check=True, capture_output=True
    )
    assert len(proc.stdout) == 0


@pytest.mark.slow
def test_annotate_add_invalid_yaml(annotations_folder):
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
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_call(["lineapy", "annotate", "add", f.name])

    proc = subprocess.run(
        ["lineapy", "annotate", "list"], check=True, capture_output=True
    )
    assert len(proc.stdout) == 0


@pytest.mark.slow
def test_annotate_add_valid_yaml(annotations_folder):
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
        subprocess.check_call(["lineapy", "annotate", "add", f.name])

    proc = subprocess.run(
        ["lineapy", "annotate", "list"], check=True, capture_output=True
    )
    assert len(str(proc.stdout).split("\n")) == 1


@pytest.mark.slow
def test_annotate_delete_invalid_path(tmp_path, annotations_folder):
    """
    Verifies failure of deleting non-existent source.
    """
    invalid_path = tmp_path / "nonexistent.yaml"
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(
            ["lineapy", "annotate", "delete", "-n", str(invalid_path)]
        )


@pytest.mark.slow
def test_delete_existing_source(annotations_folder):
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
        subprocess.check_call(["lineapy", "annotate", "add", f.name])

    source_name = os.path.basename(f.name)
    source_name = remove_annotations_file_extension(source_name)
    source_name = slugify(source_name)
    subprocess.check_call(
        [
            "lineapy",
            "annotate",
            "delete",
            "--name",
            os.path.basename(source_name),
        ]
    )
    proc = subprocess.run(
        ["lineapy", "annotate", "list"], check=True, capture_output=True
    )
    assert len(proc.stdout) == 0


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
