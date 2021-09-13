import pytest

import lineapy.app.app_db
from lineapy import ExecutionMode
from tests.util import setup_db, TEST_ARTIFACT_NAME


@pytest.fixture(autouse=True)
def test_db_mock(monkeypatch):
    test_db = setup_db(ExecutionMode.TEST, reset=True)
    monkeypatch.setattr(lineapy.app.app_db, "lineadb", test_db)


def test_executor_and_db_apis(test_db_mock):
    from lineapy.app.app_db import lineadb

    r = lineadb.find_artifact_by_name(TEST_ARTIFACT_NAME)
    assert r is not None and len(r) == 1
    # FIXME: add more assetions
