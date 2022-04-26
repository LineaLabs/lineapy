# type: ignore
import ast
import sys

import pytest

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
    import asttokens

    tree = ast.parse(code)
    # ensure that the end_lineno is not available and fetching it raises exceptions
    with pytest.raises(AttributeError):
        print(tree.body[0].end_lineno)

    # now we invoke the SourceGiver and add end_linenos in 2 steps - first we run the tree thr asttokens
    asttokens.ASTTokens(code, parse=False, tree=tree)
    # double check that the line numbers cooked up by asttokens are correct
    assert tree.body[0].last_token.end[0] == lineno

    # and in step 2, run the tree thr SourceGiver and copy the asttokens's token values
    # so that the tree looks like 3.8+ tree with all the end_linenos etc
    SourceGiver().transform(tree)
    assert tree.body[0].end_lineno == lineno
