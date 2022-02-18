from datetime import datetime
from unittest.mock import MagicMock

import pytest

from lineapy.graph_reader.apis import LineaArtifact
from lineapy.utils.constants import VERSION_DATE_STRING


def test_artifact_without_version_has_version():
    artifact = LineaArtifact(
        db=MagicMock(),
        execution_id=MagicMock(),
        node_id=MagicMock(),
        session_id=MagicMock(),
        name="test_artifact_without_version_has_version",
    )
    assert artifact.version is not None
    # doing this stupid thing because test sometimes fails when second part changes
    assert artifact.version == datetime.now().strftime(VERSION_DATE_STRING)


@pytest.mark.xfail(reason="named version is not supported yet")
def test_with_named_version_has_version():
    artifact = LineaArtifact(
        db=MagicMock(),
        execution_id=MagicMock(),
        node_id=MagicMock(),
        session_id=MagicMock(),
        name="test_with_named_version_same_as_default",
        # version="2020-01-01T00:00:00",
    )
    assert artifact.version == "2020-01-01T00:00:00"

    artifact2 = LineaArtifact(
        db=MagicMock(),
        execution_id=MagicMock(),
        node_id=MagicMock(),
        session_id=MagicMock(),
        name="test_with_named_version",
        # version="test_version",
    )
    assert artifact2.version == "test_version"
