from pathlib import Path

from fsspec.core import url_to_fs
from fsspec.implementations.local import LocalFileSystem

from lineapy.utils.config import options


def test_artifact_storage_dir_type():
    """
    Making sure the path we are setting is correct typing, so pandas.io.common.get_handler can process it correctly.
    """
    old_artifact_storage_dir = options.safe_get("artifact_storage_dir")
    options.set(
        "artifact_storage_dir",
        "/tmp/somelineapytestprefix/",
    )
    assert isinstance(
        url_to_fs(str(options.safe_get("artifact_storage_dir")))[0],
        LocalFileSystem,
    )

    options.set(
        "artifact_storage_dir",
        Path("~").expanduser().resolve(),
    )
    assert isinstance(
        url_to_fs(str(options.safe_get("artifact_storage_dir")))[0],
        LocalFileSystem,
    )

    options.set("artifact_storage_dir", old_artifact_storage_dir)
