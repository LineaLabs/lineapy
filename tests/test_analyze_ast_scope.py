from lineapy.transformer.analyze_ast_scope import (
    analyze_ast_scope,
    Scope,
)
import pytest
import ast
import astpretty


EXAMPLES: list[tuple[str, Scope]] = [
    ("[x for x in xx]", Scope(loaded={"xx"})),
    ("[x for x in xx if y]", Scope(loaded={"xx", "y"})),
    ("[x for xx in xxx for x in xx]", Scope(loaded={"xxx"})),
    # Verify that conditionals only end up having unbound variables
    # if they are not defined in one of their parent scopes.
    ("[x for xx in xxx if x for x in xx]", Scope(loaded={"xxx", "x"})),
    ("[x for xx in xxx for x in xx if x]", Scope(loaded={"xxx"})),
    ("x.y", Scope(loaded={"x"})),
]


@pytest.mark.parametrize("code,scope", EXAMPLES)
def test_analyze_ast_scope(code: str, scope: Scope):
    a = ast.parse(code).body[0]
    assert analyze_ast_scope(a) == scope, astpretty.pformat(a)
