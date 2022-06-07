from lineapy.db.utils import is_artifact_version_valid


def test_is_artifact_version_valid():
    cases = (
        (-1, False),
        (-102, False),
        (1, True),
        (0, True),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
        (0.3, False),
        (3.0, False),
        (1.0, False),
        ("all", True),
        ("latest", True),
        ("al", False),
        ("lattest", False),
        ("1", True),
        ("3", True),
        ("5", True),
        ("0.3", False),
        ("1.1", False),
    )

    for version, is_valid in cases:
        assert is_artifact_version_valid(version) == is_valid
