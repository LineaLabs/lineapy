import pathlib

import pytest
import upath

from lineapy.utils.config import options


def test_artifact_storage_dir_type():
    """
    Making sure the path we are setting is correct typing, so pandas.io.common.get_handler can process it correctly.
    """
    options.set(
        "artifact_storage_dir",
        "s3://somelineapytestbucket/somelineapytestprefix/",
    )
    assert isinstance(
        options.safe_get("artifact_storage_dir"),
        upath.implementations.cloud.S3Path,
    )

    options.set(
        "artifact_storage_dir",
        "/tmp/somelineapytestprefix/",
    )
    assert isinstance(
        options.safe_get("artifact_storage_dir"), pathlib.PosixPath
    )

    options.set("artifact_storage_dir", "~")
    assert isinstance(
        options.safe_get("artifact_storage_dir"), pathlib.PosixPath
    )
