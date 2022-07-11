from unittest.mock import MagicMock

import pytest

from lineapy.api.api_utils import de_lineate_code

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
        pytest.param(
            "x = lineapy.get('x').get_value()",
            f"""import pickle
x = pickle.load(open("{FAKE_PATH}","rb"))""",
            id="lineapy_get",
        ),
        pytest.param(
            """import lineapy
x = lineapy.get('x').get_value()
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
    db = MagicMock()
    db.get_node_value_path = MagicMock(return_value=FAKE_PATH)  # type: ignore
    delineazed = de_lineate_code(code, db)
    assert delineazed == expected
