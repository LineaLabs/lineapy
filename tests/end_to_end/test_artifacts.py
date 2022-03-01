from datetime import datetime

from lineapy.utils.constants import VERSION_DATE_STRING


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
    assert res.values["art_version"] == datetime.now().strftime(
        VERSION_DATE_STRING
    )
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
    assert len(db_values) == 4
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
    assert db_values[1]["artifact_version"].startswith(
        datetime.now().strftime("%Y-%m-%dT%H:%M:")
    )
    # finally make sure the print property is updated to reflect versions
    assert res.values["all_print"] == "\n".join(
        [
            f"{v['artifact_name']}:{v['artifact_version']} created on {v['date_created']}"
            for v in db_values
        ]
    )
