import pytest

from lineapy.cli import cli


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("xyz", "xyz"),
        ("test.yml", "test.yml"),
        ("test.yaml", "test"),
        ("test.annotations.yaml", "test"),
        ("tet.annotation.yaml", "tet.annotation"),
        ("tet.annotation.yml", "tet.annotation.yml"),
        ("explicit .yaml", "explicit"),
        ("implicit . annotations . yaml", "implicit"),
    ],
)
def test_remove_annotations_file_extension(test_input, expected):

    assert cli.remove_annotations_file_extension(test_input) == expected
