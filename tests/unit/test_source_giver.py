#
#
# type: ignore
import ast
import sys

import asttokens
import pytest
from astpretty import pprint

from lineapy.transformer.source_giver import SourceGiver


@pytest.mark.parametrize(
    "code,lineno",
    [
        (
            """a = 10
b = lambda x: x + 10
c = b(a)
""",
            1,
        ),
        ("""a = 10;b=10""", 1),
    ],
    ids=["multiline", "singleline"],
)
def test_source_giver_adds_end_lineno(code, lineno):
    if sys.version_info >= (3, 8):
        pytest.skip("SourceGiver not invoked for Python 3.8+")
    tree = ast.parse(code)
    with pytest.raises(AttributeError):
        print(tree.body[0].end_lineno)

    asttokens.ASTTokens(code, parse=False, tree=tree)
    pprint(tree)
    print(tree.body[0].last_token)
    assert tree.body[0].last_token.end[0] == lineno

    SourceGiver().transform(tree)
    assert tree.body[0].end_lineno == lineno
    print(tree)
