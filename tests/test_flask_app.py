import pytest

import lineapy.app.app_db
from lineapy import ExecutionMode
from tests.util import setup_db, TEST_ARTIFACT_NAME


def test_executor_and_db_apis():
    db = setup_db(ExecutionMode.TEST, reset=True)
    r = db.find_artifact_by_name(TEST_ARTIFACT_NAME)
    assert r is not None and len(r) == 1
    # FIXME: add more assetions
