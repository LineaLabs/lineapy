from unittest.mock import MagicMock

import pytest

from lineapy.graph_reader.apis import LineaArtifact

FAKE_PATH = "/tmp/path/to/value/file/xey"


@pytest.mark.parametrize(
    "code, expected",
    [
        pytest.param("", "", id="blank"),
        pytest.param("x = 1", "x = 1", id="nolinea"),
        pytest.param(
            """import lineapy
lineapy.save(x,"xey")""",
            f"""import pickle
pickle.dump(x,open("{FAKE_PATH}","wb"))""",
            id="lineapy_save",
        ),
        (
            "x = lineapy.get('x').get_value()",
            f"""import pickle
x = pickle.load(open("{FAKE_PATH}","rb"))""",
            id="lineapy_get",
        ),
        pytest.param(
            """import lineapy
x = lineapy.get('x').value
y = lineapy.get('y')""",
            f"""import pickle
import lineapy
x = pickle.load(open("{FAKE_PATH}","rb"))
y = lineapy.get('y')""",
            id="lineapy_get_partial_replace",
        ),
    ],
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
