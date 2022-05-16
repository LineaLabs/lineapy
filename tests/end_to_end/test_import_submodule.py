import os
import shutil

import pytest

from lineapy.exceptions.user_exception import UserException
from lineapy.utils.utils import prettify


@pytest.fixture(scope="function", autouse=True)
def preconfigure(tmp_path):
    shutil.copytree("tests/end_to_end/import_data", tmp_path / "import_data")
    os.chdir(tmp_path)
    yield


def test_error_not_imported(execute):
    """
    Verify that trying to access a not imported submodule raises an AttributeError
    """
    code = """import import_data.utils
some_var = import_data.utils.__will_not_import.some_var
"""
    with pytest.raises(UserException):
        execute(code, snapshot=False)


def test_from(execute):
    """
    Test import a submodule from a parent
    """
    code = """from import_data.utils import __no_imported_submodule
is_prime = __no_imported_submodule.is_prime
"""
    res = execute(code, artifacts=["is_prime"])
    assert res.values["is_prime"] is False
    assert res.artifacts["is_prime"] == prettify(code)


def test_direct(tmp_path, execute):
    """
    Test importing a submodule and referring to it directly
    """
    code = """import import_data.utils.__no_imported_submodule
is_prime = import_data.utils.__no_imported_submodule.is_prime
"""
    res = execute(code, artifacts=["is_prime"])
    assert res.values["is_prime"] is False
    assert res.artifacts["is_prime"] == prettify(code)


def test_slice_parent(execute):
    """
    Test that slicing on a submodule should remove the import for the parent
    """
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


def test_slice_sibling(execute):
    """
    Test importing a submodule and referring to it directly, should have a different slice
    """
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
