from lineapy.cli import cli


def test_remove_annotations_file_extension():
    items = (
        ("xyz", "xyz"),
        ("test.yml", "test.yml"),
        ("test.yaml", "test"),
        ("test.annotations.yaml", "test"),
        ("tet.annotation.yaml", "tet.annotation"),
        ("tet.annotation.yml", "tet.annotation.yml"),
        ("explicit .yaml", "explicit"),
        ("implicit . annotations . yaml", "implicit"),
    )

    for value, output in items:
        assert cli.remove_annotations_file_extension(value) == output
