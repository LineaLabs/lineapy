import os
import shutil

import pytest

# @pytest.fixture(scope="session", autouse=True)
# def preconfigure(tmp_path):
#     shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
#     os.chdir(tmp_path)


def test_from(tmp_path, execute):
    """
    Test import a submodule from a parent
    """
    shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
    os.chdir(tmp_path)
    code = """from import_data.utils import __no_imported_submodule
is_prime = __no_imported_submodule.is_prime
"""
    res = execute(code, artifacts=["is_prime"])
    assert res.values["is_prime"] is False
    assert res.artifacts["is_prime"] == code


def test_direct(tmp_path, execute):
    """
    Test importing a submodule and referring to it directly
    """
    shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
    os.chdir(tmp_path)

    code = """import import_data.utils.__no_imported_submodule
is_prime = import_data.utils.__no_imported_submodule.is_prime
"""
    res = execute(code, artifacts=["is_prime"])
    assert res.values["is_prime"] is False
    assert res.artifacts["is_prime"] == code


def test_error_not_imported(tmp_path, execute):
    """
    Verify that trying to access a not imported submodule raises an AttributeError
    """
    shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
    os.chdir(tmp_path)

    code = """import import_data.utils
is_prime = import_data.utils.__no_imported_submodule.is_prime
"""
    with pytest.raises(AttributeError):
        execute(code, snapshot=False)


def test_slice_parent(tmp_path, execute):
    """
    Test that slicing on a submodule should remove the import for the parent
    """
    shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
    os.chdir(tmp_path)

    code = """import import_data.utils.__no_imported_submodule
import import_data.utils
is_prime = import_data.utils.__no_imported_submodule.is_prime
"""
    res = execute(code, artifacts=["is_prime"])
    assert res.values["is_prime"] is False
    assert (
        res.artifacts["is_prime"]
        == """import import_data.utils.__no_imported_submodule
is_prime = import_data.utils.__no_imported_submodule.is_prime
"""
    )


def test_slice_sibling(tmp_path, execute):
    """
    Test importing a submodule and referring to it directly, should have a different slice
    """
    shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
    os.chdir(tmp_path)

    code = """import import_data.utils.__no_imported_submodule
import import_data.utils.__no_imported_submodule_prime
first_is_prime = import_data.utils.__no_imported_submodule.is_prime
second_is_prime = import_data.utils.__no_imported_submodule_prime.is_prime
"""
    res = execute(code, artifacts=["first_is_prime", "second_is_prime"])
    assert res.values["first_is_prime"] is False
    assert res.values["second_is_prime"] is True
    assert (
        res.artifacts["first_is_prime"]
        == """import import_data.utils.__no_imported_submodule
import import_data.utils.__no_imported_submodule_prime
first_is_prime = import_data.utils.__no_imported_submodule.is_prime
"""
    )
    assert (
        res.artifacts["second_is_prime"]
        == """import import_data.utils.__no_imported_submodule
import import_data.utils.__no_imported_submodule_prime
second_is_prime = import_data.utils.__no_imported_submodule_prime.is_prime
"""
    )
