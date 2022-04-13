from datetime import datetime, timedelta

import pytest

from lineapy.utils.constants import VERSION_DATE_STRING


def test_simple_slice(execute):
    SIMPLE_SLICE = """import lineapy
a = 2
b = 2
c = min(b,5)
b
lineapy.save(c, "c")
"""
    res = execute(
        SIMPLE_SLICE,
        snapshot=False,
    )

    assert res.slice("c") == """b = 2\nc = min(b,5)\n"""


def test_set_one_artifact(execute):
    code = """import lineapy
x = []
lineapy.save(x, "x")
"""
    res = execute(code, snapshot=False)
    assert res.slice("x") == "x = []\n"


def test_overwrite_artifact(execute):
    code = """import lineapy
x = []
lineapy.save(x, "x")
x = 10
lineapy.save(x, "x")
"""
    res = execute(code, snapshot=False)
    assert res.slice("x") == "x = 10\n"


def test_alias_artifact(execute):
    code = """import lineapy
x = []
lineapy.save(x, "x")
lineapy.save(x, "x2")
"""
    res = execute(code, snapshot=False)
    assert res.slice("x") == "x = []\n"
    assert res.slice("x2") == "x = []\n"


def test_bad_artifact_save_fails_and_recovers(execute):
    code = """import pandas
import lineapy
x=1
y=1
lineapy.save(pandas,"fails")
lineapy.save(x,"works")
lineapy.save(y,"workstoo")
"""
    res = execute(code, snapshot=False)
    assert res.values["x"] == 1


def test_get_artifact_has_version(execute):
    code = """import lineapy
x = 1
lineapy.save(x, "x")
art = lineapy.get("x")
art_version = art.version
"""
    res = execute(code, snapshot=False)
    # Verify the version date is at most a minute from now but not in the future
    artifact_version_delta = datetime.now() - datetime.fromisoformat(
        res.values["art_version"]
    )
    assert timedelta(minutes=0) < artifact_version_delta < timedelta(minutes=1)
    assert res.slice("x") == "x = 1\n"


def test_catalog_shows_all_versions(execute):
    code = """import lineapy
from time import sleep
x = 1
lineapy.save(x, "x")
sleep(1)
lineapy.save(x, "x")
catalog = lineapy.catalog()
all_artifacts = catalog.export
all_print = catalog.print
"""
    res = execute(code, snapshot=False)
    db_values = res.values["all_artifacts"]
    assert len(db_values) == 2
    # ensure that both the artifacts have same name and value
    assert db_values[0]["artifact_name"] == "x"
    assert db_values[1]["artifact_name"] == "x"
    # verify that the versions are different
    assert db_values[1]["artifact_version"] != db_values[0]["artifact_version"]
    # verifty that the versions are datestrings and in correct order
    assert datetime.strptime(
        db_values[0]["artifact_version"], VERSION_DATE_STRING
    ) < datetime.strptime(
        db_values[1]["artifact_version"], VERSION_DATE_STRING
    )
    # also verify that the date_created is in the right order.
    # artifact_version and date_created might not match esp in future with named versions
    # but for default version it should be a string version of a date
    assert db_values[0]["date_created"] < db_values[1]["date_created"]

    # Verify the version date is at most a minute old but not in the future
    artifact_version_delta = datetime.now() - datetime.fromisoformat(
        db_values[1]["artifact_version"]
    )
    assert timedelta(minutes=0) < artifact_version_delta < timedelta(minutes=1)

    # finally make sure the print property is updated to reflect versions
    assert res.values["all_print"] == "\n".join(
        [
            f"{v['artifact_name']}:{v['artifact_version']} created on {v['date_created']}"
            for v in db_values
        ]
    )


def test_artifact_session_code(execute):
    importl = """import lineapy
"""
    artifact_f_save = """
lineapy.save(y, "deferencedy")
use_y = lineapy.get("deferencedy")
"""
    code_body = """y = []
x = [y]
y.append(10)
x[0].append(11)
# this should not show up
print(x)"""
    tracer = execute(importl + code_body + artifact_f_save, snapshot=False)
    artifact = tracer.values["use_y"]
    assert artifact.get_session_code() == importl + code_body + artifact_f_save
    assert (
        artifact.db.get_session_context(
            artifact._session_id
        ).environment_type.name
        == "SCRIPT"
    )


@pytest.mark.xfail(
    reason="fails because the reexecution of graph created a new random file that saves the value of cleanedx"
)
def test_artifact_code_without_lineapy(execute):
    code = """import lineapy
x = 1
savepath = lineapy.save(x, "cleanedx")
cleanedx = lineapy.get("cleanedx").value
y = cleanedx + 1
y_art = lineapy.save(y, "y")
"""
    t2 = execute(code, snapshot=False)
    saved_path = t2.values["savepath"]._get_value_path()
    artifact = t2.values["y_art"]
    assert (
        artifact.get_code()
        == """import lineapy
cleanedx = lineapy.get("cleanedx").value
y = cleanedx + 1
"""
    )
    assert (
        artifact.get_code(False)
        == f"""import pickle
import lineapy
cleanedx = pickle.load(open("{saved_path}", "rb"))
y = cleanedx + 1
"""
    )
