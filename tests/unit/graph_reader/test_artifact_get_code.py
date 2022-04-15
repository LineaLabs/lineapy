from unittest.mock import MagicMock

import pytest

from lineapy.graph_reader.apis import LineaArtifact

FAKE_PATH = "/tmp/path/to/value/file/xey"


@pytest.mark.parametrize(
    "code, expected",
    [
        ("", ""),
        ("x = 1", "x = 1"),
        (
            'lineapy.save(x,"xey")',
            f"""import pickle
pickle.dump(x,open("{FAKE_PATH}","wb"))""",
        ),
        (
            "x = lineapy.get('x').value",
            f"""import pickle
x = pickle.load(open("{FAKE_PATH}","rb"))""",
        ),
    ],
    ids=["blank", "nolinea", "lineapy_save", "lineapy_get"],
)
def test__de_linealize_code(code, expected):
    artifact = LineaArtifact(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    artifact._get_value_path = MagicMock(  # type: ignore
        return_value=FAKE_PATH
    )
    lineazed = artifact._de_linealize_code(code, True)
    delineazed = artifact._de_linealize_code(code, False)
    assert lineazed == code
    assert delineazed == expected
