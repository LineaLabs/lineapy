from lineapy.db.utils import is_artifact_version_valid, parse_artifact_version

import pytest


def test_parse_artifact_version():
    cases = (
        (-1, False),
        (-102, False),
        (1, True),
        (0, True),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
        (0.3, True),
        (3.0, True),
        (1.0, True),
        ("all", True),
        ("latest", True),
        ("al", False),
        ("lattest", False),
        ("1", True),
        ("3", True),
        ("5", True),
        ("0.3", True),
        ("1.1", True),
    )
    for version, is_valid in cases:
        if is_valid:
            parse_artifact_version(version)
        else:
            print(version)
            with pytest.raises(ValueError):
                parse_artifact_version(version)

