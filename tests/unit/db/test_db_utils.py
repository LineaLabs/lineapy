import pytest

from lineapy.db.utils import parse_artifact_version


def test_parse_artifact_version():
    cases = (
        (-1, False, None),
        (-102, False, None),
        (1, True, 1),
        (0, True, 0),
        (2, True, 2),
        (3, True, 3),
        (4, True, 4),
        (5, True, 5),
        (0.3, True, 0),
        (3.0, True, 3),
        (1.0, True, 1),
        ("all", True, "all"),
        ("latest", True, "latest"),
        ("al", False, None),
        ("lattest", False, None),
        ("1", True, 1),
        ("3", True, 3),
        ("5", True, 5),
        ("0.3", True, 0),
        ("1.1", True, 1),
    )
    for version, is_valid, expected in cases:
        if is_valid:
            assert parse_artifact_version(version) == expected
        else:
            print(version)
            with pytest.raises(ValueError):
                parse_artifact_version(version)
