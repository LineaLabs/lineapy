import os
import shutil
import subprocess
import tempfile

import pytest

from lineapy.cli.cli import remove_annotations_file_extension
from lineapy.plugins.utils import slugify
from lineapy.utils.config import CUSTOM_ANNOTATIONS_FOLDER_NAME, linea_folder


@pytest.mark.slow
def test_cli_entrypoint():
    """
    Verifies that the "--help" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(["lineapy", "--help"])


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
        subprocess.check_call(
            [
                "lineapy",
                "python",
                f.name,
                "--slice",
                "first_arg",
                "--arg",
                "an arg",
            ]
        )


@pytest.mark.slow
def test_slice_housing():
    """
    Verifies that the "--slice" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(
        ["lineapy", "python", "tests/housing.py", "--slice", "p value"]
    )


@pytest.mark.slow
def test_slice_housing_multiple():
    """
    Verifies that we can run "--slice" CLI command multiple times
    """
    subprocess.check_call(
        [
            "lineapy",
            "python",
            "tests/housing.py",
            "--slice",
            "p value",
            "--slice",
            "y",
        ]
    )


@pytest.mark.slow
def test_export_slice_housing():
    """
    Verifies that the "--export-slice" CLI command is aliased to the `lineapy` executable
    """
    subprocess.check_call(
        [
            "lineapy",
            "python",
            "tests/housing.py",
            "--slice",
            "p value",
            "--export-slice",
            "sliced_housing",
        ]
    )


@pytest.mark.slow
def test_export_slice_housing_multiple():
    """
    Verifies that we can run "--export-slice" CLI command multiple times
    """
    subprocess.check_call(
        [
            "lineapy",
            "python",
            "tests/housing.py",
            "--slice",
            "p value",
            "--export-slice",
            "p_value_housing",
            "--slice",
            "y",
            "--export-slice",
            "y_housing",
        ]
    )


@pytest.fixture
def annotations_folder():
    """
    Fixture for annotate commands. It moves user's
    '.lineapy/custom-annotations'dir and
    replaces it with a temp for testing.
    """
    path = linea_folder() / CUSTOM_ANNOTATIONS_FOLDER_NAME
    path_str = str(path.resolve())
    stash_path = linea_folder() / (CUSTOM_ANNOTATIONS_FOLDER_NAME + ".old")
    stash_path_str = str(stash_path.resolve())
    shutil.move(path_str, stash_path_str)

    yield path

    shutil.rmtree(path_str)
    shutil.move(stash_path_str, path_str)


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
        ["lineapy", "python", str(f)], capture_output=True
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
